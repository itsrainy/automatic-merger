
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer, subprocess, os, json


CONFIG_FILE = "merger-config.json"
WORKING_DIR = ""

class SimpleServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        # TODO: Audit for possible security implications
        content_length = int(self.headers['Content-Length']) 
        branch_info = json.loads(self.rfile.read(content_length))
        process_new_commit(branch_info["repo"], branch_info["branch"])
    
        self._set_headers()
        self.wfile.write("Repo: " + branch_info["repo"] + "\n" + "Branch: " + branch_info["branch"])

def run(server_class=HTTPServer, handler_class=SimpleServer, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

# Pulled from https://codereview.stackexchange.com/a/86067
# Needs validation
def cyclic(g):
    """Return True if the directed graph g has a cycle.
    g must be represented as a dictionary mapping vertices to
    iterables of neighbouring vertices. For example:

    >>> cyclic({1: (2,), 2: (3,), 3: (1,)})
    True
    >>> cyclic({1: (2,), 2: (3,), 3: (4,)})
    False

    """
    path = set()

    def visit(vertex):
        path.add(vertex)
        for neighbour in g.get(vertex, ()):
            if neighbour in path or visit(neighbour):
                return True
        path.remove(vertex)
        return False

    return any(visit(v) for v in g)

def construct_graph(edges):
    g = {}
    for edge in edges:
        if edge["from"] not in g:
            g[edge["from"]] = []
        g[edge["from"]].append(edge["to"])
    return g

def recursively_merge(branch_name, g):
    if branch_name not in g:
        return
    
    # Ensure that the branch exists locally and is up to date
    subprocess.call(["git", "checkout", branch_name])
    subprocess.call(["git", "pull"])
    for b in g[branch_name]:
        subprocess.call(["git", "checkout", b]) 
        subprocess.call(["git", "merge", branch_name])
        recursively_merge(b, g)

def process_new_commit(repository, branch_name):
    if os.getcwd() != WORKING_DIR:
        os.chdir(WORKING_DIR)

    conf = {}
    repo_conf = None
    with open(CONFIG_FILE) as conf_file:
        conf = json.loads(conf_file.read())
    for repo in conf["repositories"]:
        if repo["name"] == repository:
            repo_conf = repo
    if repo_conf == None:
        raise Exception("Specified repository doesn't exist in our config")
    print("Loaded config and found repo")

    # Check if repo exists, if not clone it
    if not os.path.isdir(repo_conf["locationOnDisk"]):
        print("Cloning repo...")
        subprocess.call(["git", "clone", repo_conf["url"], repo_conf["locationOnDisk"]])
    
    print("Changing directory to specified repo")
    os.chdir(repo_conf["locationOnDisk"]) # Will this try to switch into a deeper folder each time?
    
    print("Updating specified repo")
    subprocess.call(["git", "pull"])

    # Validate graph
    g = construct_graph(repo_conf["edges"])
    if cyclic(g):
        # email user to let them know?
        # Ideally we'd never get into this state if we validate on user input
        raise Exception("Branch graph for specified repo is cyclic. Aborting")

    if branch_name in g:
        recursively_merge(branch_name, g)
    
    # Using --all for now, but we'll want to make this a bit more surgical
    subprocess.call(["git", "checkout", "master"])
    subprocess.call(["git", "push", "--all"])

def main():
    from sys import argv
    global WORKING_DIR
    WORKING_DIR = os.getcwd()
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

if __name__ == "__main__":
    main()    