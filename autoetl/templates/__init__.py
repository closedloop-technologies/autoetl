def get_templates(fname):
    try:
        with open(fname) as f:
            return f.read()
    except FileNotFoundError:
        return None
