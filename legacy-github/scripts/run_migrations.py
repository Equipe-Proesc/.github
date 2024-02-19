import os
import pathlib
import subprocess


def main() -> None:
    variables = [x for x in os.environ if x.startswith('CI_')]
    lines_php = ['<?php', 'return array(']
    lines_env = []
    for variable in variables:
        lines_php.append(f"'{variable}' => '{os.getenv(variable)}',")
        lines_env.append(f"{variable}='{os.getenv(variable)}'")
    lines_php.append(');')
    pathlib.Path('.env.php').write_text('\n'.join(lines_php), 'utf-8')
    pathlib.Path('.env.local.php').write_text('\n'.join(lines_php), 'utf-8')
    pathlib.Path('.env').write_text('\n'.join(lines_env), 'utf-8')

    migrations_dirs = [x for x in subprocess.check_output(['ls', 'app/database/migrations']).decode('utf-8').split('\n')
                       if x != '' and x != 'niteroi'][-2:]
    for dir_ in migrations_dirs:
        subprocess.call(
            ['php', 'artisan', 'migrate', f'--path=app/database/migrations/{dir_}', '--force']
        )


if __name__ == '__main__':
    main()
