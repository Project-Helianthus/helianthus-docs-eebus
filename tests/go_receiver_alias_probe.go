package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"go/types"
	"os"
	"sort"
	"strings"
)

const (
	probePackagePath = "example.invalid/helianthus/synthetic/receiverprobe"
	foreignPath      = "example.invalid/helianthus/synthetic/foreign"
)

type probeImporter struct{}

func (probeImporter) Import(path string) (*types.Package, error) {
	if path != foreignPath {
		return nil, fmt.Errorf("unexpected import path %q", path)
	}
	pkg := types.NewPackage(path, "foreign")
	object := types.NewTypeName(token.NoPos, pkg, "External", nil)
	types.NewNamed(object, types.NewStruct(nil, nil), nil)
	if pkg.Scope().Insert(object) != nil {
		panic("duplicate synthetic import object")
	}
	pkg.MarkComplete()
	return pkg, nil
}

type checkedPackage struct {
	file *ast.File
	info *types.Info
	pkg  *types.Package
}

type receiverObject struct {
	Base           string   `json:"base"`
	Pointer        bool     `json:"pointer"`
	TypeParameters []string `json:"type_parameters"`
}

type positiveVector struct {
	Name                   string         `json:"name"`
	DeclaredReceiver       string         `json:"declared_receiver"`
	ASTType                string         `json:"ast_type"`
	GoTypesReceiver        string         `json:"go_types_receiver"`
	AliasHops              int            `json:"alias_hops"`
	NamedMethodOccurrences int            `json:"named_method_occurrences"`
	Receiver               receiverObject `json:"receiver"`
	Signature              string         `json:"signature"`
}

type identityVector struct {
	BaseParameterNames            []string `json:"base_parameter_names"`
	ReceiverParameterNames        []string `json:"receiver_parameter_names"`
	ArgumentsMatchReceiverObjects []bool   `json:"arguments_match_receiver_objects"`
	ReceiverObjectsDifferFromBase []bool   `json:"receiver_objects_differ_from_base"`
}

type negativeVector struct {
	Name     string `json:"name"`
	GoTypes  string `json:"go_types"`
	Producer string `json:"producer"`
}

type probeOutput struct {
	GoVersion       string           `json:"go_version"`
	NamedNumMethods int              `json:"named_num_methods"`
	Positive        []positiveVector `json:"positive"`
	Identity        identityVector   `json:"identity"`
	Negative        []negativeVector `json:"negative"`
}

type normalizedReceiver struct {
	receiverObject
	aliasHops int
}

func check(source string) (*checkedPackage, []error) {
	fileSet := token.NewFileSet()
	file, err := parser.ParseFile(
		fileSet,
		"probe.go",
		source,
		parser.SkipObjectResolution,
	)
	if err != nil {
		return nil, []error{err}
	}

	info := &types.Info{
		Types: make(map[ast.Expr]types.TypeAndValue),
		Defs:  make(map[*ast.Ident]types.Object),
		Uses:  make(map[*ast.Ident]types.Object),
	}
	errors := make([]error, 0)
	config := types.Config{
		GoVersion: "go1.24",
		Importer:  probeImporter{},
		Error: func(err error) {
			errors = append(errors, err)
		},
	}
	pkg, err := config.Check(
		probePackagePath,
		fileSet,
		[]*ast.File{file},
		info,
	)
	if err != nil && len(errors) == 0 {
		errors = append(errors, err)
	}
	return &checkedPackage{file: file, info: info, pkg: pkg}, errors
}

func requireChecked(source string) *checkedPackage {
	checked, errors := check(source)
	if len(errors) != 0 {
		panic(errors[0])
	}
	return checked
}

func receiverExpr(declaration *ast.FuncDecl) ast.Expr {
	if declaration.Recv == nil || len(declaration.Recv.List) != 1 {
		panic("method does not have exactly one receiver field")
	}
	return declaration.Recv.List[0].Type
}

func receiverSpelling(expression ast.Expr) string {
	switch node := expression.(type) {
	case *ast.Ident:
		return node.Name
	case *ast.StarExpr:
		return "*" + receiverSpelling(node.X)
	case *ast.IndexExpr:
		return receiverSpelling(node.X) + "[" + receiverSpelling(node.Index) + "]"
	case *ast.IndexListExpr:
		arguments := make([]string, len(node.Indices))
		for index, argument := range node.Indices {
			arguments[index] = receiverSpelling(argument)
		}
		return receiverSpelling(node.X) + "[" + strings.Join(arguments, ", ") + "]"
	default:
		panic(fmt.Sprintf("unsupported receiver expression %T", expression))
	}
}

func typeListLen(list *types.TypeList) int {
	if list == nil {
		return 0
	}
	return list.Len()
}

func typeParamListLen(list *types.TypeParamList) int {
	if list == nil {
		return 0
	}
	return list.Len()
}

func isASCIIExported(name string) bool {
	return len(name) > 0 && name[0] >= 'A' && name[0] <= 'Z'
}

func normalizeReceiver(
	typ types.Type,
	pkg *types.Package,
	owner *types.Named,
) (normalizedReceiver, error) {
	aliases := make(map[*types.Alias]bool)
	pointers := 0
	aliasHops := 0

	for {
		if typ == nil {
			return normalizedReceiver{}, fmt.Errorf("invalid receiver type")
		}
		switch node := typ.(type) {
		case *types.Pointer:
			pointers++
			if pointers > 1 {
				return normalizedReceiver{}, fmt.Errorf("more than one pointer")
			}
			typ = node.Elem()
		case *types.Alias:
			if aliases[node] {
				return normalizedReceiver{}, fmt.Errorf("receiver alias cycle")
			}
			aliases[node] = true
			aliasHops++
			object := node.Obj()
			if object == nil || object.Pkg() != pkg || object.Parent() != pkg.Scope() {
				return normalizedReceiver{}, fmt.Errorf("foreign receiver alias")
			}
			if typeParamListLen(node.TypeParams()) != 0 || typeListLen(node.TypeArgs()) != 0 {
				return normalizedReceiver{}, fmt.Errorf("generic receiver alias")
			}
			typ = node.Rhs()
		case *types.Named:
			origin := node.Origin()
			if origin == nil || origin.Obj() == nil || origin.Obj().Pkg() != pkg ||
				origin.Obj().Parent() != pkg.Scope() {
				return normalizedReceiver{}, fmt.Errorf("foreign receiver base")
			}
			if !isASCIIExported(origin.Obj().Name()) {
				return normalizedReceiver{}, fmt.Errorf("unexported receiver base")
			}
			if origin != owner {
				return normalizedReceiver{}, fmt.Errorf("receiver owner mismatch")
			}
			switch origin.Underlying().(type) {
			case *types.Pointer:
				return normalizedReceiver{}, fmt.Errorf("defined pointer receiver base")
			case *types.Interface:
				return normalizedReceiver{}, fmt.Errorf("interface receiver base")
			}
			if aliasHops != 0 && typeListLen(node.TypeArgs()) != 0 {
				return normalizedReceiver{}, fmt.Errorf("instantiated receiver alias")
			}
			return normalizedReceiver{
				receiverObject: receiverObject{
					Base:           origin.Obj().Name(),
					Pointer:        pointers == 1,
					TypeParameters: []string{},
				},
				aliasHops: aliasHops,
			}, nil
		case *types.Basic:
			if node.Kind() == types.Invalid {
				return normalizedReceiver{}, fmt.Errorf("invalid receiver type")
			}
			return normalizedReceiver{}, fmt.Errorf("invalid receiver terminal %T", typ)
		default:
			return normalizedReceiver{}, fmt.Errorf("invalid receiver terminal %T", typ)
		}
	}
}

func methodOccurrences(owner *types.Named, method *types.Func) int {
	count := 0
	for index := 0; index < owner.NumMethods(); index++ {
		if owner.Method(index) == method {
			count++
		}
	}
	return count
}

func unnamedTuple(tuple *types.Tuple) *types.Tuple {
	variables := make([]*types.Var, tuple.Len())
	for index := 0; index < tuple.Len(); index++ {
		variable := tuple.At(index)
		variables[index] = types.NewVar(token.NoPos, variable.Pkg(), "", variable.Type())
	}
	return types.NewTuple(variables...)
}

func receiverFreeType(signature *types.Signature, pkg *types.Package) string {
	withoutReceiver := types.NewSignatureType(
		nil,
		nil,
		nil,
		unnamedTuple(signature.Params()),
		unnamedTuple(signature.Results()),
		signature.Variadic(),
	)
	return types.TypeString(withoutReceiver, types.RelativeTo(pkg))
}

func positiveVectors() (int, []positiveVector) {
	checked := requireChecked(`package receiverprobe

type ReceiverBase struct{}
type ReceiverDirect = ReceiverBase
type ReceiverChain = ReceiverDirect
type ReceiverPointer = *ReceiverBase

func (ReceiverDirect) AliasDirect(value uint8) uint8 { return value }
func (ReceiverChain) AliasChained(value string) string { return value }
func (ReceiverPointer) AliasPointer(value bool) bool { return value }
func (*ReceiverDirect) AliasExplicitPointer(value int32) int32 { return value }
`)
	owner := checked.pkg.Scope().Lookup("ReceiverBase").Type().(*types.Named)
	vectors := make([]positiveVector, 0, owner.NumMethods())
	for _, declaration := range checked.file.Decls {
		methodDeclaration, ok := declaration.(*ast.FuncDecl)
		if !ok || methodDeclaration.Recv == nil {
			continue
		}
		method, ok := checked.info.Defs[methodDeclaration.Name].(*types.Func)
		if !ok {
			panic("method declaration has no *types.Func definition")
		}
		expression := receiverExpr(methodDeclaration)
		normalized, err := normalizeReceiver(checked.info.TypeOf(expression), checked.pkg, owner)
		if err != nil {
			panic(err)
		}
		signature := method.Type().(*types.Signature)
		pointer := ""
		if normalized.Pointer {
			pointer = "*"
		}
		typeText := receiverFreeType(signature, checked.pkg)
		vectors = append(vectors, positiveVector{
			Name:                   method.Name(),
			DeclaredReceiver:       receiverSpelling(expression),
			ASTType:                fmt.Sprintf("%T", checked.info.TypeOf(expression)),
			GoTypesReceiver:        types.TypeString(signature.Recv().Type(), types.RelativeTo(checked.pkg)),
			AliasHops:              normalized.aliasHops,
			NamedMethodOccurrences: methodOccurrences(owner, method),
			Receiver:               normalized.receiverObject,
			Signature: fmt.Sprintf(
				"func (%s%s) %s%s",
				pointer,
				normalized.Base,
				method.Name(),
				typeText[len("func"):],
			),
		})
	}
	sort.Slice(vectors, func(left, right int) bool {
		return vectors[left].Name < vectors[right].Name
	})
	return owner.NumMethods(), vectors
}

func identityProbe() identityVector {
	checked := requireChecked(`package receiverprobe

var T3 uint8
type BlankSlots[_, T1, _ any] struct{}
func (BlankSlots[A, B, C]) Bind(A, B, C) (A, B, C) { panic("probe") }
`)
	owner := checked.pkg.Scope().Lookup("BlankSlots").Type().(*types.Named)
	method := owner.Method(0)
	signature := method.Type().(*types.Signature)
	receiverNamed, ok := signature.Recv().Type().(*types.Named)
	if !ok {
		panic("generic receiver is not *types.Named")
	}

	length := owner.TypeParams().Len()
	result := identityVector{
		BaseParameterNames:            make([]string, length),
		ReceiverParameterNames:        make([]string, length),
		ArgumentsMatchReceiverObjects: make([]bool, length),
		ReceiverObjectsDifferFromBase: make([]bool, length),
	}
	if signature.RecvTypeParams().Len() != length || receiverNamed.TypeArgs().Len() != length {
		panic("generic receiver arity mismatch")
	}
	for index := 0; index < length; index++ {
		base := owner.TypeParams().At(index)
		receiver := signature.RecvTypeParams().At(index)
		result.BaseParameterNames[index] = base.Obj().Name()
		result.ReceiverParameterNames[index] = receiver.Obj().Name()
		result.ArgumentsMatchReceiverObjects[index] = receiverNamed.TypeArgs().At(index) == receiver
		result.ReceiverObjectsDifferFromBase[index] = receiver != base
	}
	return result
}

func requireTypeCheckRejection(name, source, diagnostic string) negativeVector {
	_, errors := check(source)
	if len(errors) == 0 {
		panic(name + " unexpectedly type-checked")
	}
	for _, err := range errors {
		if strings.Contains(err.Error(), diagnostic) {
			return negativeVector{Name: name, GoTypes: "REJECT", Producer: "REJECT"}
		}
	}
	panic(fmt.Sprintf("%s did not report %q: %v", name, diagnostic, errors))
}

func unexportedBaseVector() negativeVector {
	checked := requireChecked(`package receiverprobe

type hidden struct{}
type Receiver = hidden
func (Receiver) Exported() {}
`)
	owner := checked.pkg.Scope().Lookup("hidden").Type().(*types.Named)
	for _, declaration := range checked.file.Decls {
		method, ok := declaration.(*ast.FuncDecl)
		if !ok || method.Recv == nil {
			continue
		}
		_, err := normalizeReceiver(checked.info.TypeOf(receiverExpr(method)), checked.pkg, owner)
		if err == nil || err.Error() != "unexported receiver base" {
			panic(fmt.Sprintf("unexpected unexported-base normalization: %v", err))
		}
		return negativeVector{
			Name:     "unexported-base",
			GoTypes:  "PASS",
			Producer: "REJECT unexported receiver base",
		}
	}
	panic("unexported-base method declaration not found")
}

func negativeVectors() []negativeVector {
	return []negativeVector{
		requireTypeCheckRejection(
			"alias-cycle",
			"package receiverprobe\ntype Receiver = Cycle\ntype Cycle = Receiver\nfunc (Receiver) Bad() {}\n",
			"invalid recursive type",
		),
		requireTypeCheckRejection(
			"defined-pointer-base",
			"package receiverprobe\ntype ReceiverBase *int\ntype Receiver = ReceiverBase\nfunc (Receiver) Bad() {}\n",
			"invalid receiver type",
		),
		requireTypeCheckRejection(
			"foreign-base",
			"package receiverprobe\nimport foreign \""+foreignPath+"\"\ntype Receiver = foreign.External\nfunc (Receiver) Bad() {}\n",
			"cannot define new methods on non-local type",
		),
		requireTypeCheckRejection(
			"generic-alias",
			"package receiverprobe\ntype ReceiverBase[T any] struct{}\ntype Receiver[T any] = ReceiverBase[T]\nfunc (Receiver[T]) Bad() {}\n",
			"cannot define new methods on generic alias type",
		),
		requireTypeCheckRejection(
			"instantiated-alias",
			"package receiverprobe\ntype ReceiverBase[T any] struct{}\ntype Receiver = ReceiverBase[int]\nfunc (Receiver) Bad() {}\n",
			"cannot define new methods on instantiated type",
		),
		requireTypeCheckRejection(
			"interface-base",
			"package receiverprobe\ntype ReceiverBase interface{}\ntype Receiver = ReceiverBase\nfunc (Receiver) Bad() {}\n",
			"invalid receiver type",
		),
		requireTypeCheckRejection(
			"invalid-base",
			"package receiverprobe\ntype Receiver = Missing\nfunc (Receiver) Bad() {}\n",
			"undefined: Missing",
		),
		requireTypeCheckRejection(
			"more-than-one-pointer",
			"package receiverprobe\ntype ReceiverBase struct{}\ntype ReceiverPointer = *ReceiverBase\nfunc (*ReceiverPointer) Bad() {}\n",
			"invalid receiver type *ReceiverPointer",
		),
		unexportedBaseVector(),
	}
}

func main() {
	namedNumMethods, positive := positiveVectors()
	output := probeOutput{
		GoVersion:       "go1.24",
		NamedNumMethods: namedNumMethods,
		Positive:        positive,
		Identity:        identityProbe(),
		Negative:        negativeVectors(),
	}
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetEscapeHTML(false)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(output); err != nil {
		panic(err)
	}
}
