import libcst as cst
import random
import hashlib
from typing import Dict, Set, List, Optional
from pathlib import Path

class NameGenerator:
    """
    Generates deterministic names based on a seed.
    Supports themes: 'gibberish' (default), 'fantasy'.
    """
    def __init__(self, seed: int, theme: str = "gibberish"):
        self.rng = random.Random(seed)
        self.theme = theme
        self.generated: Set[str] = set()

        # Fantasy Theme Vocabulary
        # Fantasy Theme Vocabulary
        self.fantasy_prefixes = [
            "Crystal", "Shadow", "Thunder", "Void", "Iron", "Mist", "Star", "Blood", "Frost", "Flame",
            "Obsidian", "Azure", "Crimson", "Verdant", "Golden", "Silver", "Ebon", "Ivory", "Arcane", "Spirit",
            "Soul", "Mind", "Heart", "Bone", "Ash", "Ember", "Storm", "Rain", "Wind", "Sea"
        ]
        self.fantasy_suffixes = [
            "Blade", "Shield", "Weaver", "Walker", "Caller", "Binder", "Warden", "Seeker", "Breaker", "Singer",
            "Dancer", "Stalker", "Hunter", "Mage", "Knight", "Lord", "King", "Queen", "Prince", "Sage",
            "Guard", "Watcher", "Keeper", "Bringer", "Slayer", "Eater", "Drinker", "Forged", "Born", "Kin"
        ]
        self.fantasy_verbs = [
            "invoke", "summon", "banish", "enchant", "forge", "shatter", "weave", "scry", "transmute", "bind",
            "call", "cast", "channel", "conjure", "craft", "create", "curse", "bless", "empower", "imbue",
            "infuse", "invoke", "kindle", "mending", "purify", "restore", "ward", "seal", "open", "close"
        ]

    def generate(self, original_name: str, kind: str = "obj") -> str:
        """
        Generates a new name for the given original name.
        'kind' can be 'class', 'function', or 'constant' to guide casing.
        """
        while True:
            if self.theme == "fantasy":
                new_name = self._generate_fantasy(original_name, kind)
            else:
                new_name = self._generate_gibberish(original_name)
            
            if new_name not in self.generated and new_name != original_name:
                self.generated.add(new_name)
                return new_name

    def _generate_gibberish(self, original_name: str) -> str:
        # Create a hash of the name + salt to pick letters
        h = hashlib.md5(original_name.encode() + str(self.rng.random()).encode()).hexdigest()
        prefix = "c_" if original_name[0].isupper() else "f_"
        suffix = h[:6]
        return f"{prefix}{suffix}"

    def _generate_fantasy(self, original_name: str, kind: str) -> str:
        if kind == "class":
            return f"{self.rng.choice(self.fantasy_prefixes)}{self.rng.choice(self.fantasy_suffixes)}"
        elif kind == "function":
             verb = self.rng.choice(self.fantasy_verbs)
             noun = self.rng.choice(self.fantasy_suffixes).lower()
             return f"{verb}_{noun}"
        else: # variables / misc
             return self.rng.choice(self.fantasy_prefixes).lower() + "_" + self.rng.choice(self.fantasy_prefixes).lower()

class SymbolCollector(cst.CSTVisitor):
    """
    First pass: Collects top-level definitions to be renamed.
    """
    def __init__(self):
        self.defined_classes: Set[str] = set()
        self.defined_functions: Set[str] = set()

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.defined_classes.add(node.name.value)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        name = node.name.value
        if name.startswith("__") and name.endswith("__"):
            return
            
        # Blocklist common built-in methods to prevent accidental renaming of dict/list/str/set/file methods
        protected = {
            'add', 'append', 'as_integer_ratio', 'bit_count', 'bit_length', 'capitalize', 'casefold', 'center', 'clear', 
            'conjugate', 'copy', 'count', 'denominator', 'difference', 'difference_update', 'discard', 'encode', 'endswith', 
            'expandtabs', 'extend', 'find', 'format', 'format_map', 'from_bytes', 'fromhex', 'fromkeys', 'get', 'hex', 'imag', 
            'index', 'insert', 'intersection', 'intersection_update', 'is_integer', 'isalnum', 'isalpha', 'isascii', 'isdecimal', 
            'isdigit', 'isdisjoint', 'isidentifier', 'islower', 'isnumeric', 'isprintable', 'isspace', 'issubset', 'issuperset', 
            'istitle', 'isupper', 'items', 'join', 'keys', 'ljust', 'lower', 'lstrip', 'maketrans', 'numerator', 'partition', 
            'pop', 'popitem', 'real', 'remove', 'removeprefix', 'removesuffix', 'replace', 'reverse', 'rfind', 'rindex', 'rjust', 
            'rpartition', 'rsplit', 'rstrip', 'setdefault', 'sort', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 
            'symmetric_difference', 'symmetric_difference_update', 'title', 'to_bytes', 'translate', 'union', 'update', 'upper', 
            'values', 'zfill',
            # File / IO methods
            'read', 'write', 'close', 'open', 'flush', 'seek', 'tell', 'readline', 'readlines', 'writelines',
            # Context manager
            '__enter__', '__exit__',
            # Common argument names that might interact with external libraries via kwargs
            'name', 'params', 'extra', 'kwargs', 'kwarg', 'args', 'self', 'cls', 'target', 'source', 
            'callback', 'ctx', 'environ', 'start_response', 'exc_info',
        }
        if name in protected:
            return

        self.defined_functions.add(name)

class SymbolRenamer(cst.CSTTransformer):
    """
    Second pass: Renames definitions and usages.
    Validates against the 'mapping' dictionary.
    """
    def __init__(self, mapping: Dict[str, str], internal_prefixes: List[str]):
        self.mapping = mapping
        self.internal_prefixes = internal_prefixes
        self.external_names: Set[str] = set()
        
        # Standard built-ins that we should treat as external if used as bases for attribute access
        self.external_names.update(["sys", "os", "json", "math", "re", "typing", "t"])

    def _is_internal_module(self, module_node: Optional[cst.BaseExpression]) -> bool:
        if not module_node:
            return False # "from . import x" -> relative=1 works, module=None. 
        # But import_from handles relative flag separately.
        # This helper is for the string checks.
        
        parts = []
        curr = module_node
        while isinstance(curr, cst.Attribute):
            parts.append(curr.attr.value)
            curr = curr.value
        if isinstance(curr, cst.Name):
            parts.append(curr.value)
        
        full_name = ".".join(reversed(parts))
        for prefix in self.internal_prefixes:
            if full_name == prefix or full_name.startswith(prefix + "."):
                return True
        return False

    def visit_Import(self, node: cst.Import) -> None:
        for alias in node.names:
            # Check if this import is internal
            # alias.name is the module name (e.g. 'json' or 'flask.app')
            # alias.asname is the bound name
            mod_name_node = alias.name
            is_internal = self._is_internal_module(mod_name_node)
            
            if not is_internal:
                # Mark the bound name as external
                if alias.asname:
                    if isinstance(alias.asname.name, cst.Name):
                        self.external_names.add(alias.asname.name.value)
                else:
                    # 'import json' -> 'json' is external
                    # 'import os.path' -> 'os' is external? strict import?
                    # usually top level name is bound.
                    parts = []
                    curr = mod_name_node
                    while isinstance(curr, cst.Attribute):
                        parts.append(curr.attr.value)
                        curr = curr.value
                    if isinstance(curr, cst.Name):
                        self.external_names.add(curr.value)

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        is_internal = False
        if node.relative:
            is_internal = True
        elif node.module:
            is_internal = self._is_internal_module(node.module)
            
        if not is_internal:
            # All imported names are external
            for alias in node.names:
                if isinstance(alias, cst.ImportAlias):
                    if alias.asname:
                        if isinstance(alias.asname.name, cst.Name):
                            self.external_names.add(alias.asname.name.value)
                    else:
                        if isinstance(alias.name, cst.Name):
                            self.external_names.add(alias.name.value)

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        if original_node.name.value in self.mapping:
            return updated_node.with_changes(name=cst.Name(self.mapping[original_node.name.value]))
        return updated_node

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        if original_node.name.value in self.mapping:
            return updated_node.with_changes(name=cst.Name(self.mapping[original_node.name.value]))
        return updated_node

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        # Handle func() calls
        if isinstance(updated_node.func, cst.Name) and updated_node.func.value in self.mapping:
             return updated_node.with_changes(func=cst.Name(self.mapping[updated_node.func.value]))
        return updated_node
    
    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        # Handle loose usage (e.g. in annotations or assignments)
        if original_node.value in self.mapping:
            return updated_node.with_changes(value=self.mapping[original_node.value])
        return updated_node

    def leave_Attribute(self, original_node: cst.Attribute, updated_node: cst.Attribute) -> cst.Attribute:
        # If the object (value) is one of our tracked external names, do NOT rename the attribute.
        # Check original_node.value to see the name used.
        base_name = None
        if isinstance(original_node.value, cst.Name):
            base_name = original_node.value.value
        
        if base_name and base_name in self.external_names:
            # Revert the attribute change if any
            return updated_node.with_changes(attr=original_node.attr)
            
        return updated_node

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
         # 1. Revert the module name in all cases (we don't rename files/modules)
         updated_node = updated_node.with_changes(module=original_node.module)

         # 2. Revert external imports
         is_internal = False
         if original_node.relative:
             is_internal = True
         elif original_node.module:
             is_internal = self._is_internal_module(original_node.module)
        
         if not is_internal:
             # External import! Revert the names (aliases) too.
             return updated_node.with_changes(names=original_node.names)
         
         return updated_node

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        # For 'import X', X is a module/file. We don't rename files.
        # So we must always revert the name 'X'.
        # However, if 'import X as Y', 'Y' is a bound name in this scope.
        # If 'Y' was collected and mapped (unlikely with current collector), we should keep 'Y' renamed.
        # But 'X' must be original.
        
        new_names = []
        for orig_alias, updated_alias in zip(original_node.names, updated_node.names):
            # Restore the module name.
            # We keep the updated_alias.asname (if any renames happened there).
            new_alias = updated_alias.with_changes(name=orig_alias.name)
            new_names.append(new_alias)
            
        return updated_node.with_changes(names=new_names)

class Mutator:
    def __init__(self, seed: int, theme: str = "gibberish", internal_prefixes: List[str] = None):
        self.generator = NameGenerator(seed, theme)
        self.mapping: Dict[str, str] = {}
        self.internal_prefixes = internal_prefixes or []

    def collect_definitions(self, source_code: str) -> None:
        """Pass 1: Parse code and register new symbols."""
        wrapper = cst.MetadataWrapper(cst.parse_module(source_code))
        collector = SymbolCollector()
        wrapper.visit(collector)
        
        # Generate mappings for new symbols
        for cls_name in sorted(collector.defined_classes):
            if cls_name not in self.mapping:
                self.mapping[cls_name] = self.generator.generate(cls_name, kind="class")
        
        for func_name in sorted(collector.defined_functions):
            if func_name not in self.mapping:
                self.mapping[func_name] = self.generator.generate(func_name, kind="function")

    def transform_code(self, source_code: str) -> str:
        """Pass 2: Rename symbols based on existing mapping."""
        # Note: We re-parse here. In a stricter implementation we might cache the tree.
        tree = cst.parse_module(source_code)
        transformer = SymbolRenamer(self.mapping, self.internal_prefixes)
        new_tree = tree.visit(transformer)
        return new_tree.code

    def mutate_source(self, source_code: str) -> str:
        """
        Convenience method to collect definitions and transform code in one go.
        Note: If using the same mutator instance across multiple files,
        call collect_definitions on all of them first if you want shared symbols (though this class is designed for per-file or shared mapping).
        """
        self.collect_definitions(source_code)
        return self.transform_code(source_code)

def mutate_directory(input_dir: Path, output_dir: Path, mutator: Optional[Mutator] = None, **mutator_kwargs) -> None:
    """
    Recursively helps mutate a directory of Python files.
    
    Args:
        input_dir: Path to the directory to mutate.
        output_dir: Directory to save the mutated files.
        mutator: Optional pre-configured Mutator instance.
        **mutator_kwargs: Arguments to pass to Mutator constructor if mutator is not provided.
    """
    if mutator is None:
        mutator = Mutator(**mutator_kwargs)
        
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory {input_path} does not exist.")
        
    python_files = list(input_path.rglob("*.py"))
    
    # Pass 1: Collect
    for src_file in python_files:
        with open(src_file, "r", encoding="utf-8") as f:
            code = f.read()
        mutator.collect_definitions(code)
        
    # Pass 2: Transform
    for src_file in python_files:
        rel_path = src_file.relative_to(input_path)
        dest_file = output_path / rel_path
        
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(src_file, "r", encoding="utf-8") as f:
            code = f.read()
        
        mutated_code = mutator.transform_code(code)
        
        with open(dest_file, "w", encoding="utf-8") as f:
            f.write(mutated_code)

