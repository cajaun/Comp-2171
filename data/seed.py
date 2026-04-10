import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from data.db import SessionLocal, init_db, engine
from data.models import Base, Category, Item, User, StockAdjust, ItemCondition, SlowMovingOverstock, Report


Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed_data():
    print("Seeding data...")
    

    db.query(SlowMovingOverstock).delete()
    db.query(Report).delete() 
    db.query(ItemCondition).delete()
    db.query(StockAdjust).delete()
    db.query(Item).delete()
    db.query(Category).delete()
    db.query(User).delete()
    db.commit()


    admin = User(username="admin", password_hash="admin123", role="Admin") 
    staff = User(username="staff", password_hash="staff123", role="Staff")
    db.add_all([admin, staff])
    db.commit()
    
    users = [admin, staff]


    categories_data = [
        "Beverages", "Bag Juice", "Snacks", "Tinned Food", "Breakfast Items",
        "Dry Goods", "Seasonings & Spices", "Cleaning Supplies", "Toiletries",
        "Baby Products", "Hardware Basics", "Electronics Accessories",
        "Cosmetics & Beauty", "Frozen Goods", "School Supplies"
    ]
    
    categories = {}
    for name in categories_data:
        cat = Category(name=name, description=f"Wholesale {name}")
        db.add(cat)
        categories[name] = cat
    db.commit()


    products_data = [
        # Beverages
        ("WATA 500ml", "Beverages", 60.00, 500, "Bottle"),
        ("WATA 1.5L", "Beverages", 150.00, 200, "Bottle"),
        ("Ting 330ml", "Beverages", 120.00, 300, "Bottle"),
        ("Ginger Beer", "Beverages", 130.00, 250, "Bottle"),
        ("Lasco Soy Drink", "Beverages", 180.00, 150, "Can"),
        ("Chubby Grape", "Beverages", 50.00, 400, "Bottle"),
        ("Chubby Kola", "Beverages", 50.00, 400, "Bottle"),
        ("Bigga Grape", "Beverages", 80.00, 300, "Bottle"),
        ("Bigga Pineapple", "Beverages", 80.00, 300, "Bottle"),
        ("CranWATA", "Beverages", 100.00, 250, "Bottle"),
        
        # Bag Juice
        ("Bag Juice – Grape", "Bag Juice", 20.00, 1000, "Bag"),
        ("Bag Juice – Orange", "Bag Juice", 20.00, 1000, "Bag"),
        ("Bag Juice – Cherry", "Bag Juice", 20.00, 1000, "Bag"),
        ("Bag Juice – Fruit Punch", "Bag Juice", 20.00, 1000, "Bag"),
        
        # Snacks
        ("Guava Cheese", "Snacks", 150.00, 100, "Pack"),
        ("National Cream Crackers", "Snacks", 250.00, 200, "Pack"),
        ("Excelsior Water Crackers (Big Foot)", "Snacks", 300.00, 150, "Pack"),
        ("Banana Chips", "Snacks", 100.00, 500, "Pack"),
        ("Plantain Chips", "Snacks", 100.00, 500, "Pack"),
        ("Tamarind Balls", "Snacks", 80.00, 200, "Pack"),
        ("Coconut Drops", "Snacks", 120.00, 150, "Pack"),
        ("Gizzada", "Snacks", 150.00, 100, "Pack"),
        
        # Tinned Food
        ("Canned Mackerel", "Tinned Food", 180.00, 300, "Tin"),
        ("Corned Beef", "Tinned Food", 450.00, 200, "Tin"),
        ("Sardines", "Tinned Food", 150.00, 400, "Tin"),
        ("Canned Vienna Sausage", "Tinned Food", 120.00, 350, "Tin"),
        ("Ackee (Tin)", "Tinned Food", 800.00, 100, "Tin"),
        ("Callaloo (Tin)", "Tinned Food", 250.00, 150, "Tin"),
        ("Baked Beans", "Tinned Food", 140.00, 200, "Tin"),
        
        # Breakfast Items
        ("Supligen", "Breakfast Items", 250.00, 200, "Can"),
        ("Ovaltine", "Breakfast Items", 600.00, 100, "Jar"),
        ("Milo 400g", "Breakfast Items", 550.00, 150, "Pack"),
        ("Cornflakes", "Breakfast Items", 400.00, 120, "Box"),
        ("Oats 500g", "Breakfast Items", 300.00, 150, "Pack"),
        ("Condensed Milk", "Breakfast Items", 220.00, 250, "Tin"),
        
        # Dry Goods
        ("Counter Flour 2kg", "Dry Goods", 300.00, 500, "Bag"),
        ("Counter Sugar 1kg", "Dry Goods", 200.00, 600, "Bag"),
        ("Counter Rice 2kg", "Dry Goods", 350.00, 500, "Bag"),
        ("Cornmeal 1kg", "Dry Goods", 150.00, 300, "Bag"),
        ("Red Peas 500g", "Dry Goods", 250.00, 200, "Pack"),
        
        # Seasonings & Spices
        ("Seasoned Salt", "Seasonings & Spices", 100.00, 400, "Bottle"),
        ("Maggi Cubes", "Seasonings & Spices", 500.00, 100, "Pack"),
        ("Curry Powder", "Seasonings & Spices", 150.00, 300, "Pack"),
        ("Black Pepper", "Seasonings & Spices", 120.00, 300, "Pack"),
        ("Jerk Seasoning (Jar)", "Seasonings & Spices", 450.00, 150, "Jar"),
        ("All Purpose Seasoning", "Seasonings & Spices", 180.00, 250, "Pack"),
        
        # Cleaning Supplies
        ("Bleach 1L", "Cleaning Supplies", 200.00, 200, "Bottle"),
        ("Dishwashing Liquid 500ml", "Cleaning Supplies", 250.00, 200, "Bottle"),
        ("Laundry Detergent Powder", "Cleaning Supplies", 350.00, 150, "Pack"),
        ("Fabric Softener", "Cleaning Supplies", 400.00, 100, "Bottle"),
        ("Floor Polish", "Cleaning Supplies", 500.00, 80, "Tin"),
        
        # Toiletries
        ("Bath Soap – Coco", "Toiletries", 100.00, 500, "Bar"),
        ("Toilet Paper (Bulk Pack)", "Toiletries", 1200.00, 50, "Pack"),
        ("Toothpaste", "Toiletries", 300.00, 200, "Tube"),
        ("Deodorant", "Toiletries", 450.00, 150, "Stick"),
        ("Shampoo", "Toiletries", 500.00, 100, "Bottle"),
        
        # Baby Products
        ("Baby Wipes", "Baby Products", 350.00, 200, "Pack"),
        ("Diapers (Size 3)", "Baby Products", 1500.00, 100, "Pack"),
        ("Baby Powder", "Baby Products", 250.00, 150, "Bottle"),
        ("Baby Oil", "Baby Products", 300.00, 120, "Bottle"),
        
        # Hardware Basics
        ("Nails (1lb)", "Hardware Basics", 150.00, 100, "Lb"),
        ("Hammer", "Hardware Basics", 1200.00, 20, "Unit"),
        ("Screwdriver Set", "Hardware Basics", 1500.00, 30, "Set"),
        ("Paint Brush 2\"", "Hardware Basics", 300.00, 50, "Unit"),
        
        # Electronics Accessories
        ("USB Chargers", "Electronics Accessories", 500.00, 100, "Unit"),
        ("AA Batteries", "Electronics Accessories", 400.00, 200, "Pack"),
        ("AAA Batteries", "Electronics Accessories", 400.00, 200, "Pack"),
        ("Extension Cord", "Electronics Accessories", 800.00, 50, "Unit"),
        ("Headphones (Basic)", "Electronics Accessories", 1000.00, 80, "Unit"),
        
        # Cosmetics & Beauty
        ("Nail Polish", "Cosmetics & Beauty", 200.00, 150, "Bottle"),
        ("Body Lotion", "Cosmetics & Beauty", 450.00, 120, "Bottle"),
        ("Hair Food", "Cosmetics & Beauty", 350.00, 100, "Jar"),
        ("Lip Gloss", "Cosmetics & Beauty", 150.00, 200, "Tube"),
        
        # Frozen Goods (Mock)
        ("Frozen Chicken (Whole)", "Frozen Goods", 800.00, 50, "Kg"),
        ("Frozen Mixed Vegetables", "Frozen Goods", 300.00, 80, "Pack"),
        ("Ice Cream 1L", "Frozen Goods", 900.00, 40, "Tub"),
        
        # School Supplies
        ("School Books", "School Supplies", 200.00, 300, "Unit"),
        ("Pens/Pencils (dozen)", "School Supplies", 300.00, 200, "Pack"),
        ("Notebooks (Hardcover)", "School Supplies", 250.00, 250, "Unit"),
        ("Erasers", "School Supplies", 50.00, 500, "Unit"),
        ("Rulers", "School Supplies", 80.00, 300, "Unit"),
    ]

    items = []
    for name, cat_name, price, stock, unit in products_data:
      
        actual_stock = max(0, stock + random.randint(-20, 20))
        reorder = max(10, int(stock * 0.2))
        
        item = Item(
            name=name,
            category_id=categories[cat_name].category_id,
            price=price,
            current_stock=actual_stock,
            unit=unit,
            reorder_level=reorder,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(100, 365))
        )
        db.add(item)
        items.append(item)
    
    db.commit()
    

    for item in items:
        db.refresh(item)

    # Create Stock Adjustments 
    reasons = ["Delivery", "Restock", "Sale", "Return", "Damage", "Shrinkage"]
    for _ in range(50):
        item = random.choice(items)
        user = random.choice(users)
        reason = random.choice(reasons)
        
        qty = random.randint(1, 50)
        adj_type = "Increase" if reason in ["Delivery", "Restock", "Return"] else "Decrease"
        
       
        if adj_type == "Decrease" and item.current_stock < qty:
            qty = item.current_stock
            if qty == 0: continue
            
 
        if adj_type == "Increase":
            item.current_stock += qty
        else:
            item.current_stock -= qty
            
   
        date = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 60))
        
        adj = StockAdjust(
            item_id=item.item_id,
            user_id=user.user_id,
            adjust_type=adj_type,
            quantity=qty,
            reason=reason,
            created_at=date
        )
        db.add(adj)
    
    db.commit()

    # Create Conditions 
    condition_types = ["Expired", "Spoiled", "Damaged"]
    for _ in range(15):
        item = random.choice(items)
        ctype = random.choice(condition_types)
        qty = random.randint(1, 10)
        
        if item.current_stock >= qty:
            item.current_stock -= qty
            
            cond = ItemCondition(
                item_id=item.item_id,
                condition_type=ctype,
                quantity=qty,
                reason=f"{ctype} during storage",
                cost_impact=item.price * qty,
                recorded_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
            )
            db.add(cond)
            
    db.commit()

    # Slow Moving Items
    slow_items = random.sample(items, 15)
    for item in slow_items:

        old_date = datetime.now(timezone.utc) - timedelta(days=random.randint(60, 120))
        
        adj = StockAdjust(
            item_id=item.item_id,
            user_id=admin.user_id,
            adjust_type="Decrease",
            quantity=1,
            reason="Old Sale",
            created_at=old_date
        )
        db.add(adj)
        

        db.query(StockAdjust).filter(
            StockAdjust.item_id == item.item_id, 
            StockAdjust.created_at > old_date
        ).delete()
        
    db.commit()
    
    print("Seed data populated successfully!")

if __name__ == "__main__":
    seed_data()
