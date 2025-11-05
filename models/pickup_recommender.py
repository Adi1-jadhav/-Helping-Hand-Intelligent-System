def should_recommend_pickup(quantity, category, description):
    # Categories that justify pickup even if quantity = 1
    important_categories = ["Winter Wear", "Electronics", "Furniture", "Medical Equipment"]

    # Basic description quality signal
    desc_words = description.strip().split()
    is_good_description = len(desc_words) > 5 or any(keyword in description.lower() for keyword in ["usable", "working", "gently used", "durable"])

    # Pickup recommendation logic
    if int(quantity) > 1:
        return True  # Quantity alone justifies pickup
    elif category in important_categories and is_good_description:
        return True
    else:
        return False
