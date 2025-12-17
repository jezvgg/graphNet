
def singleton(cls):
    instance_map = {}
    
    if cls not in instance_map:
        instance_map = cls()
    
    return instance_map[cls]