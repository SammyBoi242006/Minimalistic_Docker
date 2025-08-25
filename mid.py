#Minimalistic Docker
#chrooting into an image

import uuid
import tarfile
import linux

import click
import os
import traceback

def _get_image_path(image_name, image_dir, image_suffix="tar"):
    return os.path.join(image_dir,os.extsep.join([image_name,image_suffix]))

def _get_container_path(container_id,container_dir, *subdir_names):
    return os.path.join(container_dir,container_id,*subdir_names)

def create_container_root(image_name,image_dir,container_id,container_dir):
    #Creates a container root by extracting an image into a new directory
    """
    Usage:
    :param image_name: image name to extract
    :param image_dir: directory to look for image tarballs in
    :param container_id: unique id
    :param container_dir: base directory of newly generated container directories
    :return: new container root directory
    :rtype: str
    """
    image_path = _get_image_path(image_name,image_dir)
    container_root = _get_container_path(container_id,container_dir,'fs')

    assert os.path.exists(image_path), 'image %s could not be located' % image_name
    if not os.path.exists(container_root):
        os.makedirs(container_root)

    with tarfile.open(image_path) as t:
        members = [mem for mem in t.getmembers()
                   if mem.type not in (tarfile.CHRTYPE, tarfile.BLKTYPE)]
        t.extractall(container_root,members=members)
    return container_root

@click.group()
def cli():
    pass

def contain(command):
    # TODO: would you like to do something before chrooting?
    # print('Created a new root fs for our container: {}'.format(new_root))

    # TODO: chroot into new_root
    # TODO: something after chrooting? (HINT: try running: python3 rd.py run -i ubuntu -- /bin/sh)
    os.execvp(command[0],command)

@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.option('--image-name','-i',default='linux',help='Image name')
@click.option('--image-dir', help='Images directory',
              default='/d/images')
@click.option('--container-dir', help='Containers directory',
              default='/d/containers')
@click.argument('Command',required=True,nargs=-1)
def run(image_name,image_dir,container_dir,command):
    pid=os.fork()
    if pid==0:
        #containment here
        try:
            contain(command)
        except Exception:
            traceback.print_exc()
            os.exit(1) # something went wrong in contain()
    # This is the parent, pid contains the PID of the forked process
    # wait for the forked child and fetch the exit status

    _, status=os.waitpid(pid,0)
    print('{} exited with status {}'.format(pid,status))

if __name__=='__main__':
    cli()