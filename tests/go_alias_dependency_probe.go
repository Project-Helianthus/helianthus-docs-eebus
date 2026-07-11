package main

import (
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"go/types"
)

type walkState struct {
	seen      map[types.Type]bool
	rhsWalked map[*types.Alias]bool
}

func (state *walkState) walk(typ types.Type) error {
	if state.seen[typ] {
		return nil
	}
	state.seen[typ] = true

	switch node := typ.(type) {
	case *types.Alias:
		for index := 0; index < node.TypeArgs().Len(); index++ {
			if err := state.walk(node.TypeArgs().At(index)); err != nil {
				return err
			}
		}

		object := node.Obj()
		switch {
		case object.Pkg() == nil && object.Parent() == types.Universe:
			// Universe aliases bypass package/export checks, not RHS traversal.
		case object.Pkg() == nil:
			return fmt.Errorf("non-universe package-less alias")
		case object.Pkg().Path() == "":
			return fmt.Errorf("invalid empty package path")
		default:
			return fmt.Errorf("probe accepts only universe aliases")
		}

		if err := state.walk(node.Rhs()); err != nil {
			return err
		}
		state.rhsWalked[node] = true
		return nil
	case *types.Interface:
		node.Complete()
		for index := 0; index < node.NumEmbeddeds(); index++ {
			if err := state.walk(node.EmbeddedType(index)); err != nil {
				return err
			}
		}
		for index := 0; index < node.NumExplicitMethods(); index++ {
			if err := state.walk(node.ExplicitMethod(index).Type()); err != nil {
				return err
			}
		}
		return nil
	case *types.Basic:
		return nil
	default:
		return fmt.Errorf("unsupported probe type %T", typ)
	}
}

func checkedAny() *types.Alias {
	fileSet := token.NewFileSet()
	file, err := parser.ParseFile(
		fileSet,
		"probe.go",
		"package probe\nvar Accepted any\n",
		parser.SkipObjectResolution,
	)
	if err != nil {
		panic(err)
	}
	config := types.Config{GoVersion: "go1.24"}
	pkg, err := config.Check(
		"example.invalid/helianthus/synthetic/probe",
		fileSet,
		[]*ast.File{file},
		nil,
	)
	if err != nil {
		panic(err)
	}
	alias, ok := pkg.Scope().Lookup("Accepted").Type().(*types.Alias)
	if !ok {
		panic("any was not represented as *types.Alias")
	}
	return alias
}

func printResult(label string, alias *types.Alias) {
	state := &walkState{
		seen:      make(map[types.Type]bool),
		rhsWalked: make(map[*types.Alias]bool),
	}
	if err := state.walk(alias); err != nil {
		fmt.Printf("%s: REJECT %v\n", label, err)
		return
	}
	fmt.Printf(
		"%s: PASS universe=%t rhs=%T rhs_walked=%t\n",
		label,
		alias.Obj().Parent() == types.Universe,
		alias.Rhs(),
		state.rhsWalked[alias],
	)
}

func main() {
	printResult("any", checkedAny())

	detached := types.NewAlias(
		types.NewTypeName(token.NoPos, nil, "Detached", nil),
		types.Typ[types.Int],
	)
	printResult("detached", detached)

	invalidPackage := types.NewPackage("", "invalid")
	emptyPath := types.NewAlias(
		types.NewTypeName(token.NoPos, invalidPackage, "Dependency", nil),
		types.Typ[types.Int],
	)
	printResult("empty-path", emptyPath)
}
