"""
Simple Forward Chaining for Horn Clauses (definite clauses).

Supports:
 - Facts: ground predicates like parent(alice, bob)
 - Rules: body (list of predicates) => head (predicate), with variables
 - Standardizing variables apart, unification, substitution
 - Iterative forward-chaining: apply rules to known facts until no new facts
 - Example included at bottom
"""

from collections import namedtuple
import itertools
import copy

# --- Data types ---
Variable = namedtuple("Variable", ["name"])
Constant = namedtuple("Constant", ["name"])
Predicate = namedtuple("Predicate", ["name", "args"])

def var(name): return Variable(name)
def const(name): return Constant(name)
def pred(name, *args): return Predicate(name, list(args))

def is_var(x): return isinstance(x, Variable)
def is_const(x): return isinstance(x, Constant)

# --- Pretty printing ---
def term_str(t):
    return f"?{t.name}" if is_var(t) else t.name

def pred_str(p):
    return f"{p.name}({', '.join(term_str(a) for a in p.args)})"

# --- Substitution utility ---
def apply_subst_term(subst, t):
    if is_var(t):
        return subst.get(t.name, t)
    return t

def apply_subst_pred(subst, p):
    return Predicate(p.name, [apply_subst_term(subst, a) for a in p.args])

# --- Standardize variables apart (unique renaming per rule application) ---
_unique_id = 0
def fresh_var_name(base):
    global _unique_id
    _unique_id += 1
    return f"{base}_{_unique_id}"

def standardize(rule):
    """Given (body_list, head), return copy with fresh variable names."""
    body, head = rule
    mapping = {}
    def rename(t):
        if is_var(t):
            if t.name not in mapping:
                mapping[t.name] = Variable(fresh_var_name(t.name))
            return mapping[t.name]
        return t
    new_body = [Predicate(b.name, [rename(a) for a in b.args]) for b in body]
    new_head = Predicate(head.name, [rename(a) for a in head.args])
    return new_body, new_head

# --- Unification (simple) ---
def unify_terms(t1, t2, subst):
    # apply current substitutions
    if is_var(t1):
        t1 = subst.get(t1.name, t1)
    if is_var(t2):
        t2 = subst.get(t2.name, t2)

    # variable cases
    if is_var(t1) and is_var(t2) and t1.name == t2.name:
        return subst
    if is_var(t1):
        new = subst.copy()
        new[t1.name] = t2
        return new
    if is_var(t2):
        new = subst.copy()
        new[t2.name] = t1
        return new
    # constants
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

# --- Forward chaining algorithm ---
def forward_chain(kb_rules, kb_facts, query=None, verbose=True):
    """
    kb_rules: list of (body_list, head_pred)
    kb_facts: list of ground Predicate
    query: optional Predicate to check entailment
    Returns: (inferred_facts_list, substitution_if_query_proved_or_None)
    """
    known = list(kb_facts)  # growing list of facts
    if verbose:
        print("Initial facts:")
        for f in known: print("  ", pred_str(f))
        if query: print("Query:", pred_str(query))
        print("-" * 50)

    while True:
        new_facts = []
        for i, rule in enumerate(kb_rules, start=1):
            body, head = standardize(rule)  # fresh copy with unique vars
            if verbose:
                print(f"Trying Rule {i}: {' ∧ '.join(pred_str(b) for b in body)} => {pred_str(head)}")
            # find candidate known facts for each literal by matching predicate name and arity
            candidates_lists = [
                [f for f in known if f.name == lit.name and len(f.args) == len(lit.args)]
                for lit in body
            ]
            if not candidates_lists:  # rule with empty body (fact)
                theta = {}
                inferred = apply_subst_pred(theta, head)
                if inferred not in known and inferred not in new_facts:
                    new_facts.append(inferred)
                continue

            # try all combinations
            for combo in itertools.product(*candidates_lists):
                theta = {}
                ok = True
                for lit, fact in zip(body, combo):
                    theta = unify_preds(lit, fact, theta)
                    if theta is None:
                        ok = False
                        break
                if not ok:
                    continue
                qprime = apply_subst_pred(theta, head)
                # check groundness (only store ground facts here)
                if any(is_var(arg) for arg in qprime.args):
                    # skip storing non-ground inferred atoms in this simple implementation
                    if verbose:
                        print("  Derived non-ground atom (skipped storing):", pred_str(qprime))
                else:
                    if all(not (qprime.name == f.name and [a.name for a in qprime.args] == [b.name for b in f.args]) for f in known+new_facts):
                        if verbose:
                            print("  Inferred:", pred_str(qprime), "using", [pred_str(c) for c in combo], "with θ =", theta)
                        new_facts.append(qprime)
                # Check if this proves the query
                if query is not None:
                    s_q = unify_preds(qprime, query, {})
                    if s_q is not None:
                        if verbose:
                            print("\n*** Query proved by:", pred_str(qprime), "with substitution", s_q)
                        return known + new_facts, s_q

        if not new_facts:
            if verbose: print("No new facts inferred; stopping.")
            return known, None
        # add new facts to known and iterate again
        known.extend(new_facts)
        if verbose:
            print("Added facts:", ", ".join(pred_str(f) for f in new_facts))
            print("-" * 50)

# --- Example usage ---
if __name__ == "__main__":
    # Facts (ground)
    facts = [
        pred("parent", const("alice"), const("bob")),
        pred("parent", const("bob"), const("charlie")),
        pred("mother", const("diana"), const("bob")),  # extra fact to show mother=>parent rule
    ]

    # Rules
    # parent(x,y) ∧ parent(y,z) => grandparent(x,z)
    r1_body = [ pred("parent", var("x"), var("y")), pred("parent", var("y"), var("z")) ]
    r1_head = pred("grandparent", var("x"), var("z"))

    # mother(x,y) => parent(x,y)
    r2_body = [ pred("mother", var("x"), var("y")) ]
    r2_head = pred("parent", var("x"), var("y"))

    rules = [ (r1_body, r1_head), (r2_body, r2_head) ]

    # Query to check
    query = pred("grandparent", const("alice"), const("charlie"))

    inferred, subst = forward_chain(rules, facts, query=query, verbose=True)

    print("\nFinal KB facts:")
    for f in inferred:
        print("  ", pred_str(f))

    if subst:
        print("\nQuery succeeded with substitution:", subst)
    else:
        print("\nQuery not proved by forward chaining.")
