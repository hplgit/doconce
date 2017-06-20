import subprocess
def format_html(filename, options):
    args = ['doconce', 'format', 'html', filename] + options
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return_value = p.wait()
    return return_value, out, err, args
