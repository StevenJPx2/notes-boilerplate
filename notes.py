from argparse import ArgumentParser
from functools import reduce
from copy import deepcopy
import os
import json
import re

DEFAULT_PATH = os.popen('echo ~/Documents/Notes').read().split('\n')[0]
hidden_json_name = ".tags"
os.makedirs(DEFAULT_PATH, exist_ok=True)

# ARGUMENTS

def setup_tags_obj():
    
    try:
        tags_obj = json.load(open(f"{DEFAULT_PATH}{os.sep}{hidden_json_name}"))
    except FileNotFoundError:
        tags_obj = {}
        with open(f"{DEFAULT_PATH}{os.sep}{hidden_json_name}", "w") as fp:
            fp.write("{}")
    
    temp_tags_obj = deepcopy(tags_obj)
    for key in tags_obj:
        for filepath in tags_obj[key]:
            if not os.path.exists(filepath):
                if len(tags_obj[key]) == 1:
                    del temp_tags_obj[key]
                else:
                    temp_tags_obj[key].remove(filepath)
    
    tags_obj = deepcopy(temp_tags_obj)
    del temp_tags_obj
    json.dump(tags_obj, open(f"{DEFAULT_PATH}{os.sep}{hidden_json_name}", "w"), indent=4, sort_keys=True)
    
    return tags_obj

def create_parser():
    parser = ArgumentParser()
    parser.add_argument("type", 
                        help='c - create a new note, s - search for notes with regex, t - show tags or search by tag, x - search through notes with context', 
                        choices='cstx')
    parser.add_argument("filename", help='Enter the name of the note if type is c, or search term if type is s|x', nargs="?")
    parser.add_argument("--subl", "-s", help='Open note in Sublime Text', action="store_true", default=True)
    parser.add_argument("--vscode", "-v", help='Open note in VSCode', action="store_true")
    parser.add_argument("--tags", "-t", help='Add tags to note if type is c or search by tags if type is t')
    parser.add_argument("--mutually-exclusive", "-me", help='Searches for notes containing all the given tags [if type is t]', action="store_true")
    
    
    return parser
    
def main():
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        tags = args.tags.split(",")
    except AttributeError:
        tags = None
        
    tags_obj = setup_tags_obj()
    
    if args.type == 's':
        for result in re.findall(args.filename, "\n".join(os.listdir(DEFAULT_PATH))):
            print(f"{DEFAULT_PATH}{os.sep}{result}")
            
    elif args.type == 't':
        if tags is None:
            print(f"Tags:")
            for tag in tags_obj:
                print(f"\t{tag}")
        
        else:
            try:
                if args.mutually_exclusive:
                    for tag in tags[:-1]:
                        print(tag.title(), end=", ")
                    print(tags[-1].title(), end="\n\n")
                    
                    for filepath in reduce(lambda x,y: x.intersection(y), [set(tags_obj[tag]) for tag in tags]):
                        print(f"\t{filepath}")
                    print(f"\n{'-'*50}")
                        
                else:
                    for tag in tags:
                        print(f"{tag.title()}\n")
                        for filepath in tags_obj[tag]:
                            print(f"\t{filepath}")
                        print(f"\n{'-'*50}")
            except KeyError:
                print(f"error: {tags} do(es) not exist.")
                raise SystemExit(1)

    elif args.type == 'x':
        print("\nNot Implemented.")

    else:
        try:
            filepath, extension = args.filename.split('.')
        except ValueError:
            filepath, extension = args.filename, None
            
        try:
            separated_filename = filepath.split(os.sep)
            filepath, filename = f"{os.sep}".join(separated_filename[:-2]), separated_filename[-1]
        except ValueError:
            filename, filepath = filepath, None
            
        full_path = f"{filepath or DEFAULT_PATH}{os.sep}{filename}.{extension or 'txt'}"
        
        with open(full_path, 'w') as fp:
            if tags is None: tags = ['misc']
            fp.write(f'tags: {str(tags)[1:-1]}\n{"-"*50}\n\n')
            
        for key in tags:
            value = tags_obj.get(key)
            if value is None:
                tags_obj[key] = [full_path]
            else:
                value.append(full_path)
                tags_obj[key] = value
            
        json.dump(tags_obj, open(f"{DEFAULT_PATH}{os.sep}{hidden_json_name}", "w"), indent=4, sort_keys=True)
            
        if args.vscode:
            os.system(f'code {full_path}')
        else:
            os.system(f'subl {full_path}')
    
    
    

if __name__ == "__main__":
    main()