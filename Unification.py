def unify(x, y, subs=None):
    if subs is None:
        subs = {}

    if x == y:
        return subs

    # If x is a variable
    if isinstance(x, str) and x.islower():
        if x in y:
            return None  # Occurs check
        subs[x] = y
        return apply_substitution(subs)

    # If y is a variable
    if isinstance(y, str) and y.islower():
        if y in x:
            return None  # Occurs check
        subs[y] = x
        return apply_substitution(subs)

    # If both are predicates (e.g., Eats(x, Apple))
    if isinstance(x, tuple) and isinstance(y, tuple):
        if x[0] != y[0] or len(x[1]) != len(y[1]):
            return None  # Predicate name or argument count mismatch
        for a, b in zip(x[1], y[1]):
            subs = unify(a, b, subs)
            if subs is None:
                return None
        return subs

    # Otherwise fail
    return None


def apply_substitution(subs):
    # Apply substitution recursively
    for var, val in subs.items():
        for v in list(subs.keys()):
            if var in str(subs[v]) and v != var:
                subs[v] = str(subs[v]).replace(var, str(val))
    return subs


# Helper to create predicate terms
def make_predicate(name, *args):
    return (name, list(args))


# Example
expr1 = make_predicate("Eats", "x", "Apple")
expr2 = make_predicate("Eats", "Riya", "y")

result = unify(expr1, expr2)

if result:
    print("Unification Successful!")
    print("Substitutions:", result)
else:
    print("Unification Failed.")
