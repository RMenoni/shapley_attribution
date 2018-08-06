from os import system, getenv
from dotenv import load_dotenv
from pathlib import Path


def main():
    load_dotenv(dotenv_path=Path('.')/'.env')
    python = getenv('PYTHON_EXE_PATH')
    system(f'{python} setup.py build_ext --inplace')
    system(f'{python} copywriters.py')
    system(f'{python} assinaturas_redshift.py')
    for conv_or_revenue in ('conversoes', 'receita'):
        for model in ('lc', 'sp', 'sf'):
            for category in ('frontend', 'backend'):
                system(f'{python} validar_assinaturas.py {conv_or_revenue} {model} {category}')
    for model in ('sp', 'sf'):
        for conv_or_revenue in ('conversoes', 'receita'):
            for category in ('frontend', 'backend'):
                system(f'del v_values_{model}_{conv_or_revenue}_{category}.pickle')
                system(f'del shapley_{model}_{conv_or_revenue}_{category}.pickle')
    for model in ('sp', 'sf'):
        for conv_or_revenue in ('conversoes', 'receita'):
            for category in ('frontend', 'backend'):
                system(f'{python} shapley_value.py {model} {conv_or_revenue} {category}')


if __name__ == '__main__':
    main()
