import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
    def __init__(self, local_dir, remote_dir):
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        print(f"Creating handler for {self.local_dir} to upload to {self.remote_dir}")

        print("Initial upload... ")
        self.upload_files()

    def on_created(self, event):
        print(f"File {event.src_path} has been created, syncing ...")
        self.upload_files()

    def on_deleted(self, event):
        print(f"File {event.src_path} has been deleted, but this is not handled")
 
    def upload_files(self):
        try:
            result = subprocess.run(['rclone','copy', self.local_dir, self.remote_dir, '-v'], check=False, capture_output=True, text=True)
#            result = subprocess.run(['rclone','copy', self.local_dir, self.remote_dir, '--dry-run'], check=False, capture_output=True, text=True)
#            print(result.args)
            print(result.stdout)
            print(result.stderr)
            if result.returncode == 0:
                print("Ran rclone successfully.")
            else:
                print("Data synchronization failed.")
        except subprocess.CalledProcessError as e:
            print(f"Error syncing data: {e}")


if __name__ == "__main__":

    print("---== Cloudsync v1.0.1 ==---\n")
    print("Verifying settings ... ", end="")

    base_dir = os.environ.get('MXLA_BASE_DIR')

    if not base_dir:
        print("no base dir defined via MXLA_BASE_DIR (e.g. /path/to/your/nextcloud/data/{user}/files/Photos/Camera/)")
        exit(1)

    target_dir = os.environ.get('MXLA_TARGET_DIR')

    if not target_dir:
        print("no target dir defined via MXLA_TARGET_DIR (e.g. secret:/{user}/fotos/Camera/)")

    users = os.environ.get('MXLA_USERS', '').split(',')

    if not users or len(users) == 0 or users[0] == '':
        print("no comma-separated users defined via MXLA_USERS")
        exit(1)

    for user in users:
        local_dir = base_dir.replace('{user}', user.strip())

        if not os.path.isdir(local_dir):
           print("directory " + local_dir + " does not exist... exiting.")
           exit(1)

    print("done")

    observer = Observer()

    for user in users:
        local_dir = base_dir.replace('{user}', user.strip())
        remote_dir = target_dir.replace('{user}', user.strip())

        event_handler = FileHandler(local_dir, remote_dir)
        observer.schedule(event_handler, path=local_dir, recursive=True)

    print("Starting observer ... ", end="")

    observer.start()

    print("done")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    print("Bye-Bye!")