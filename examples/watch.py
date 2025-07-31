from glasscandle import Watcher, Response


watch = Watcher("db.json")

watch.bioconda("samtools")
watch.pypi("requests")

@watch.response("https://api.github.com/repos/wytamma/gisaidr/releases/latest")
def gidaidr(res: Response):
    """Check the latest release of GISAIDR."""
    json = res.json()
    return json["tag_name"]


if __name__ == "__main__":
    watch.run()  # Run once