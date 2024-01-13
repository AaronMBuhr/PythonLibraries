import yaml
from datetime import datetime
from enum import Enum

class YamlDumper:
    @staticmethod
    def yaml_compatible_deepcopy(source):
        """
        Deep copy an object (may not be dict), replacing any values that can't be converted to YAML.
        """

        def process_value(value):
            """
            Convert a value to YAML, replacing it with None if it can't be converted.
            """
            print("in process_value()")
            try:
                print("keys:")
                print(value.keys())
            except:
                pass
            try:
                # Handle enum types specifically
                print("trying enum")
                if isinstance(value, Enum):
                    retval = value.name
                    print("returning value.name " + retval)
                    return retval

                print("trying datetime")
                if isinstance(value, datetime):
                    retval = value.isoformat()
                    print("returning value.isoformat() " + retval)
                    return retval

                print("trying dict")
                try:
                    retval = {k: process_value(value[k]) for k in value.keys() if not k.startswith('_')}
                    print("returning dict " + str(retval))
                    return retval
                except:
                    pass

                print("trying to_dict()")
                # Use to_dict method if available
                if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    retval = value.to_dict()
                    print("returning value.to_dict() " + str(retval))
                    return retval
                    

                # print("trying complex object")
                # # Handle complex objects
                # if hasattr(value, '__dict__'):
                    print("has __dict__")
                    # retval = {k: process_value(v) for k, v in value.__dict__.items() if not callable(v) and not k.startswith('_')}
                    # print("returning complex object " + str(retval))

                print("trying list,tuple.set")
                # Handle lists, tuples, sets
                if isinstance(value, (list, tuple, set)):
                    retval = type(value)(process_value(v) for v in value)
                    print("returning list,tuple,set " + str(retval))

                print("check if yaml serializable")
                # Check if the value is YAML serializable
                try:
                    yaml.safe_dump({"test_key": value})
                    # print("returning yaml.safe_dump " + value)
                    return value
                except yaml.YAMLError:
                    pass

            except Exception as e:
                print(f"Error processing value: {e}")
                pass

        try:
            retval = process_value(source)
            # print("returning process_value " + retval)
            return retval
        except:
            pass
            
        try:
            retval = str(source)
            print("returning str() " + retval)
            return str(retval)
        except:
            print("returning None")
            return None

    @staticmethod
    def to_yaml_compatible_str(o):
        print("in to_yaml_compatible_str()")
        return yaml.safe_dump(YamlDumper.yaml_compatible_deepcopy(o), default_flow_style=False, allow_unicode=True, sort_keys=False, width=80, indent=4)
