def read_categories(category_names, category_ids):
    with open('CATEGORIES.dat', 'r') as cats:
        for line in cats:
            line = line.strip()
            cat_name, cat_id = line.rsplit(maxsplit=1)
            category_names.append(cat_name)
            category_ids.append(cat_id)


category_names = []
category_ids = []
read_categories(category_names, category_ids)
