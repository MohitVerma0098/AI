#!/usr/bin/env python3
"""
fol_resolution.py

Single-file First-Order Logic (FOL) resolution prover (teaching/demo quality).

- Represents Variables, Constants, Predicates, Literals, Clauses
- Implements a simple unifier (MGU) for terms & predicates (no deep occurs-check)
- Binary resolution on clauses (complementary literal pairs)
- Breadth-first search of resolvents until empty clause or exhausted
- Example included: grandparent from parent facts

Run:
    python fol_resolution.py
"""

from collections import namedtuple, deque
import itertools
import copy

# --- Basic datatypes ---
Variable = namedtuple("Variable", ["name"])
Constant = namedtuple("Constant", ["name"])
Predicate = namedtuple("Predicate", ["name", "args"])  # args: list of Term
Literal = namedtuple("Literal", ["pred", "neg"])       # pred: Predicate, neg: bool

def var(name): return Variable(name)
def const(name): return Constant(name)
def pred(name, *args): return Predicate(name, list(args))
def lit(predicate, neg=False): return Literal(predicate, neg)

def is_var(x): return isinstance(x, Variable)
def is_const(x): return isinstance(x, Constant)

# --- String helpers ---
def term_str(t):
    return f"?{t.name}" if is_var(t) else t.name

def pred_str(p):
    return f"{p.name}({', '.join(term_str(a) for a in p.args)})"

def lit_str(l):
    return ("~" if l.neg else "") + pred_str(l)

def clause_str(clause):
    if not clause:
        return "⊥ (empty clause)"
    return " ∨ ".join(sorted(lit_str(l) for l in clause))

# --- Substitution helpers ---
def apply_subst_term(subst, t):
    # follow chain until ground or no mapping
    if is_var(t) and t.name in subst:
        return apply_subst_term(subst, subst[t.name])
    return t

def apply_subst_pred(subst, p):
    return Predicate(p.name, [apply_subst_term(subst, a) for a in p.args])

def apply_subst_lit(subst, literal):
    return Literal(apply_subst_pred(subst, literal.pred), literal.neg)

# --- Unification (simple MGU) ---
def unify_terms(t1, t2, subst):
    # apply existing substitutions
    if is_var(t1) and t1.name in subst:
        return unify_terms(subst[t1.name], t2, subst)
    if is_var(t2) and t2.name in subst:
        return unify_terms(t1, subst[t2.name], subst)

    if is_var(t1):
        new = subst.copy()
        new[t1.name] = t2
        return new
    if is_var(t2):
        new = subst.copy()
        new[t2.name] = t1
        return new
    if is_const(t1) and is_const(t2) and t1.name == t2.name:
        return subst
    return None

def unify_preds(p1, p2, subst=None):
    if p1.name != p2.name or len(p1.args) != len(p2.args):
        return None
    s = {} if subst is None else subst.copy()
    for a1, a2 in zip(p1.args, p2.args):
        s = unify_terms(a1, a2, s)
        if s is None:
            return None
    return s

# --- Resolution utilities ---
def resolve(clause1, clause2):
    """
    Return list of resolvents (each as frozenset of Literals) derived by resolving
    clause1 and clause2 on complementary literals.
    """
    resolvents = []
    for l1 in clause1:
        for l2 in clause2:
            if l1.pred.name == l2.pred.name and l1.neg != l2.neg and len(l1.pred.args) == len(l2.pred.args):
                theta = unify_preds(l1.pred, l2.pred, {})
                if theta is not None:
                    new_lits = []
                    for x in clause1:
                        if x != l1:
                            new_lits.append(apply_subst_lit(theta, x))
                    for x in clause2:
                        if x != l2:
                            new_lits.append(apply_subst_lit(theta, x))
                    # remove duplicates
                    cleaned = []
                    tautology = False
                    for a in new_lits:
                        # check if complementary literal exists -> tautology (skip)
                        for b in new_lits:
                            if a.pred.name == b.pred.name and a.neg != b.neg and len(a.pred.args) == len(b.pred.args):
                                # quick syntactic check: if all args are constants with same names or same var names
                                eq = all(((is_const(x) and is_const(y) and x.name == y.name) or
                                          (is_var(x) and is_var(y) and x.name == y.name))
                                         for x, y in zip(a.pred.args, b.pred.args))
                                if eq:
                                    tautology = True
                                    break
                        if tautology:
                            break
                        if a not in cleaned:
                            cleaned.append(a)
                    if tautology:
                        continue
                    resolvents.append(frozenset(cleaned))
    return resolvents

# --- Resolution search (breadth-first like) ---
def fol_resolution(kb_clauses, query_clause, verbose=True, max_iters=10000):
    """
    kb_clauses: iterable of frozenset(Literal)
    query_clause: Predicate (we attempt to prove it by contradiction)
    Returns True if query is entailed (empty clause derived), False otherwise.
    """
    clauses = set(kb_clauses)
    neg_query = frozenset([Literal(query_clause, True)])
    clauses.add(neg_query)

    if verbose:
        print("Initial clauses:")
        for c in clauses:
            print("  {", clause_str(c), "}")
        print("-" * 60)

    new = set()
    pairs_checked = set()
    agenda = deque()

    clause_list = list(clauses)
    for (i, c1), (j, c2) in itertools.combinations(enumerate(clause_list), 2):
        agenda.append((c1, c2))

    iterations = 0
    while agenda and iterations < max_iters:
        c1, c2 = agenda.popleft()
        iterations += 1
        if (c1, c2) in pairs_checked:
            continue
        pairs_checked.add((c1, c2))

        resolvents = resolve(c1, c2)
        for r in resolvents:
            if verbose:
                print(f"Resolve: {{ {clause_str(c1)} }}  with  {{ {clause_str(c2)} }}  =>  {{ {clause_str(r)} }}")
            if not r:
                if verbose:
                    print("\nEmpty clause derived. Query proven (by contradiction).")
                return True
            if r not in clauses and r not in new:
                new.add(r)
                for c in clauses:
                    agenda.append((r, c))
                for c in new:
                    agenda.append((r, c))
        if not agenda and new:
            for n in new:
                clauses.add(n)
            clause_list = list(clauses)
            new.clear()
            for (i, c1), (j, c2) in itertools.combinations(enumerate(clause_list), 2):
                if (c1, c2) not in pairs_checked:
                    agenda.append((c1, c2))

    if verbose:
        print("\nNo empty clause found within iteration limit. Query not proved.")
    return False

# --- Example KB (clauses in CNF) ---
# KB:
#   parent(alice,bob).
#   parent(bob,charlie).
#   parent(x,y) ∧ parent(y,z) => grandparent(x,z).
# Clauses (CNF):
#   { parent(alice,bob) }
#   { parent(bob,charlie) }
#   { ~parent(x,y), ~parent(y,z), grandparent(x,z) }

def build_example_kb():
    c1 = frozenset([ Literal(pred("parent", const("alice"), const("bob")), False) ])
    c2 = frozenset([ Literal(pred("parent", const("bob"), const("charlie")), False) ])
    c3 = frozenset([
        Literal(pred("parent", var("x"), var("y")), True),
        Literal(pred("parent", var("y"), var("z")), True),
        Literal(pred("grandparent", var("x"), var("z")), False),
    ])
    return [c1, c2, c3]

if __name__ == "__main__":
    kb = build_example_kb()
    query = pred("grandparent", const("alice"), const("charlie"))
    proved = fol_resolution(kb, query, verbose=True)
    print("\nResult: query", pred_str(query), "is", "ENTAILLED (proved)" if proved else "NOT PROVED")
