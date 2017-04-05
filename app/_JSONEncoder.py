# -*- coding: utf-8 -*-
"""
解决Python中JSON转换时Datetime的转换问题
"""
import json
import datetime
import dateutil.parser
import decimal

CONVERTERS = {
    'datetime': dateutil.parser.parse,
    'decimal': decimal.Decimal,
}

class MyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime,)):
            return {"val": obj.isoformat(), "type": "datetime"}
        elif isinstance(obj, (decimal.Decimal,)):
            return {"val": str(obj), "type": "decimal"}
        else:
            return super().default(obj)
            
def object_hook(obj):
    type = obj.get('type')
    if not type:
        return obj
        
    if type in CONVERTERS:
        return CONVERTERS[type](obj['val'])
    else:
        raise Exception('Unknown {}'.format(type))

"""        
def main():
    data = {
        "hello": "world",
        "thing": datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%SZ"),
        "other": decimal.Decimal(0)
    }
    thing = json.dumps(data, cls=MyJSONEncoder)
    
    print(json.loads(thing, object_hook = object_hook))

if __name__ == '__main__':
    main()        
        
 """       
        
        
        
        
        
        
        
        
    