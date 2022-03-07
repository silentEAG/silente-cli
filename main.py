import click
import yaml
import os
import re

allowed_ext = [".md", ".txt"]

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("[i] SilentE's Tools v0.0.1")
    ctx.exit()


@click.group()
@click.option('-v', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='version info')
def main():
    pass


def error(message):
    click.echo("[x] Error: " + message + ", or why not use '--help'?")
    exit()


def check_opt(name, val):
    if val == '':
        error("Option '{}' is required".format(name))


def do_format(content, built_in_type, inverse):
    changed_num = 0
    if built_in_type == "1":
        pattern = r'!(.*)\(.*\)'
        lists = re.findall(pattern, content)
        click.echo("[+] {} places found.".format(len(lists)))
        for pt in lists:
            if inverse:
                new_pt = pt.replace('{', '[')
                new_pt = new_pt.replace('}', ']')
            else:
                new_pt = pt.replace('[', '{')
                new_pt = new_pt.replace(']', '}')
            if pt != new_pt:
                changed_num += 1
            content = content.replace(pt, new_pt)

    elif built_in_type == "2":
        pattern = r'![\[|\{].*[\]|\}]\(([^\(|\)].*)\)'
        lists = re.findall(pattern, content)
        click.echo("[+] {} places found.".format(len(lists)))
        for pt in lists:
            if inverse:
                filename = local_url + os.path.basename(pt)
            else:
                filename = internet_url + os.path.basename(pt)
            if pt != filename:
                changed_num += 1
            content = content.replace(pt, filename)
    click.echo("[+] {} places changed.".format(changed_num))
    return content


def list_kinds(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("[i] There are 2 built-in types I provide now.")
    click.echo("    - Type 1: '![]()' => '!{}()', use '--inverse/-i' to reverse it.")
    click.echo("    - Type 2: local img url => internet img url, use '--inverse/-i' to reverse it.")
    ctx.exit()

def dfs_find(path):
    res = []
    file_list = os.listdir(path)
    for file in file_list:
        cur_path = os.path.join(path, file)
        if os.path.isdir(cur_path):
            res = res + dfs_find(cur_path)
        elif os.path.splitext(cur_path)[1] in allowed_ext:
            res.append(cur_path)
    return res


@click.command()
@click.option('--list', '-l', is_flag=True, callback=list_kinds,
              expose_value=False, is_eager=True, help='list all the built-in types.')
@click.option('--path', '-p', default='', help='input your file or directory.')
@click.option('--methodtype', '-m', type=click.Choice(['1', '2']), help='select how to change.')
@click.option('--inverse', '-i', is_flag=True, help='reverse this process.')
@click.option('--yes', '-y', is_flag=True, help='execute command without any asking.')
def cFormat(path, methodtype, inverse, yes):
    check_opt("--path/-p", path)
    check_opt("--methodtype/-m", methodtype)

    if os.path.isfile(path):
        if os.path.splitext(path)[1] not in allowed_ext:
            error("Your file is not a allowable file.")
        click.echo("[+] cFormat is working...")
        content = ""
        with open(path, 'rb') as f:
            content = f.read().decode()
        content = do_format(content, methodtype, inverse)
        with open(path, 'wb') as f:
            f.write(content.encode())
        click.echo("[+] cFormat has been done.")
    elif os.path.isdir(path):
        click.echo("[+] This is a directory.")
        files = dfs_find(path)
        if len(files) == 0:
            error("This directory doesn't have any file to change.")
        sure = input("[+] Find {} files in total, are you sure you want to change all files in this directory? [y/N]:".format(len(files)))
        if sure.lower() != 'y':
            exit()
        click.echo("[+] cFormat is working...")
        content = ""
        for file in files:
            with open(file, 'rb') as f:
                content = f.read().decode()
            content = do_format(content, methodtype, inverse)
            with open(file, 'wb') as f:
                f.write(content.encode())
        click.echo("[+] cFormat has been done.")
    else:
        error("No such a file or directory")
    pass


# initialize the option.
def init():
    # add information
    cur_path = os.path.dirname(os.path.realpath(__file__))
    yml = os.path.join(cur_path, "config/main.yml")
    global internet_url, local_url
    with open(yml) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        internet_url = data['url']['internet_url']
        local_url = data['url']['local_url']
    if internet_url == "" or local_url == "":
        click.echo("Please confirm your url settings.")
        exit()


def test(path):
    res = dfs_find(path)
    print(res)
    pass


main.add_command(cFormat)
if __name__ == '__main__':
    init()
    main()
    # test("E:\KnowledgeBase\Drip\Drip")
