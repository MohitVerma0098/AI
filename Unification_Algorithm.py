#!/usr/bin/env python3
"""
unify.py

Robinson-style Unification algorithm with occurs-check.

Supports:
 - Variable(name)
 - Constant(name)
 - Function(name, args...) for compound terms

Main function:
    mgu = unify(term1, term2)
Returns:
    dict mapping variable names -> terms (the substitution), or None if unification fails.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Union

# --- Term classes ---
@dataclass(frozen=True)
class Var:
    name: str
    def __repr__(self): return f"?{self.name}"

@dataclass(frozen=True)
class Const:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class Func:
    name: str
    args: tuple
    def __repr__(self):
        if not self.args:
            return self.name
        return f"{self.name}({', '.join(repr(a) for a in self.args)})"

Term = Union[Var, Const, Func]

# --- Utilities: apply substitution, occurs-check, term equality (structural) ---
def apply_subst(subst: Dict[str, Term], term: Term) -> Term:
    """Recursively apply substitution to a term. Subst is varname -> Term."""
    if isinstance(term, Var):
        if term.name in subst:
            return apply_subst(subst, subst[term.name])
        return term
    if isinstance(term, Const):
        return term
    # Func
    return Func(term.name, tuple(apply_subst(subst, a) for a in term.args))

def occurs_in(var: Var, term: Term, subst: Dict[str, Term]) -> bool:
    """Occurs-check (with current substitution): does var occur anywhere inside term?"""
    term = apply_subst(subst, term)
    if isinstance(term, Var):
        return term.name == var.name
    if isinstance(term, Const):
        return False
    return any(occurs_in(var, a, subst) for a in term.args)

# --- Unification algorithm (Robinson) ---
def unify_terms(t1: Term, t2: Term, subst: Optional[Dict[str, Term]] = None) -> Optional[Dict[str, Term]]:
    """
    Try to unify t1 and t2 under current substitution subst.
    Returns updated substitution (dict) if successful, otherwise None.
    """
    if subst is None:
        subst = {}

    # Apply current substitution first
    t1 = apply_subst(subst, t1)
    t2 = apply_subst(subst, t2)

    # If identical after substitution -> no change
    if type(t1) is type(t2) and isinstance(t1, Const) and isinstance(t2, Const) and t1.name == t2.name:
        return subst
    if isinstance(t1, Var) and isinstance(t2, Var) and t1.name == t2.name:
        return subst

    # If t1 is a variable
    if isinstance(t1, Var):
        # occurs-check
        if occurs_in(t1, t2, subst):
            return None
        new_subst = dict(subst)
        new_subst[t1.name] = t2
        return new_subst

    # If t2 is a variable
    if isinstance(t2, Var):
        if occurs_in(t2, t1, subst):
            return None
        new_subst = dict(subst)
        new_subst[t2.name] = t1
        return new_subst

    # Both are functions: must have same name and same arity
    if isinstance(t1, Func) and isinstance(t2, Func):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            return None
        s = dict(subst)
        for a1, a2 in zip(t1.args, t2.args):
            s = unify_terms(a1, a2, s)
            if s is None:
                return None
        return s

    # otherwise constants that don't match -> fail
    return None

def unify(t1: Term, t2: Term) -> Optional[Dict[str, Term]]:
    """Convenience wrapper returning the MGU for t1 and t2 (or None)."""
    return unify_terms(t1, t2, {})

# --- Pretty printer for substitution ---
def subst_str(subst: Dict[str, Term]) -> str:
    if not subst:
        return "{}"
    return "{ " + ", ".join(f"{k} -> {repr(apply_subst(subst, v))}" for k, v in subst.items()) + " }"

# --- Examples / Tests ---
if __name__ == "__main__":
    # Example 1: unify f(x, a) and f(b, y)  -> { x -> b, y -> a }
    x = Var("x")
    y = Var("y")
    a = Const("a")
    b = Const("b")
    f1 = Func("f", (x, a))
    f2 = Func("f", (b, y))
    print("Unify:", f1, "and", f2)
    s = unify(f1, f2)
    print("  MGU:", subst_str(s))
    print("  apply to f1:", apply_subst(s, f1))
    print("  apply to f2:", apply_subst(s, f2))
    print()

    # Example 2: unify parent(x, g(y)) and parent(f(a), g(b))
    x = Var("x")
    y = Var("y")
    a = Const("a")
    b = Const("b")
    gby = Func("g", (y,))
    gb = Func("g", (b,))
    fa = Func("f", (a,))
    p1 = Func("parent", (x, gby))
    p2 = Func("parent", (fa, gb))
    print("Unify:", p1, "and", p2)
    s2 = unify(p1, p2)
    print("  MGU:", subst_str(s2))
    print("  apply to p1:", apply_subst(s2, p1))
    print("  apply to p2:", apply_subst(s2, p2))
    print()

    # Example 3: occurs-check failing case: unify x and f(x) -> should fail (None)
    x = Var("x")
    fx = Func("f", (x,))
    print("Unify:", x, "and", fx)
    s3 = unify(x, fx)
    print("  MGU:", s3)   # None expected
    print()

    # Example 4: unify constants that differ -> fail
    print("Unify:", Const("a"), "and", Const("b"))
    print("  MGU:", unify(Const("a"), Const("b")))
