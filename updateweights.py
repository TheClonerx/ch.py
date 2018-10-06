import sys
import zlib
import json
import re
import io
import pprint


if sys.version_info[0] < 3:
    class urllib:
        request = __import__("urllib2")
else:
    import urllib.request


class Updater:
    def findid(self):
        url = urllib.request.urlopen("http://st.chatango.com/cfg/nc/r.json")
        if url.headers.get("Content-Encoding") == "gzip":
            print("Server weights encoded with gzip, decoding...")
            data = zlib.decompress(url.read(), 47)
        else:
            data = url.read()
        data = data.decode()
        data = json.loads(data)
        return data["r"]

    def findweights(self):
        url = urllib.request.urlopen(
            "http://st.chatango.com/h5/gz/r%s/id.html" % self.ID
        )
        print("Found server weights.")
        if url.headers.get('Content-Encoding') == "gzip":
            print("Server weights encoded with gzip, decoding...")
            data = zlib.decompress(url.read(), 47)
        else:
            data = url.read()
        print("Processing server weights...")
        data = data.decode("utf-8", "ignore").splitlines()
        tags = json.loads(data[7].split(" = ")[-1])
        weights = []
        for a, b in tags["sm"]:
            c = tags["sw"][b]
            weights.append((int(a), c))
        return weights

    def updatech(self):
        print("Writing server weights to ch.py...")
        with open("ch.py", "r+") as ch:
            rdata = ch.read()
            if sys.version_info[0] == 3:
                formated = io.StringIO()
                kwargs = {"compact": True}
            else:
                kwargs = {}
                formated = io.BytesIO()
            pprint.pprint(self.weights, formated, 4, 79, None, **kwargs)
            formated.seek(0)
            formated = formated.read()
            formated = formated.replace("[   ", "[\n    ")
            formated = formated.replace("]", "\n]")
            formated = "tsweights = %s\n\n" % formated
            wdata = re.sub(
                r"tsweights = \[.*?\]\s*", formated,
                rdata,
                flags=re.M | re.S
            )
            ch.seek(0)
            ch.write(wdata)
            ch.truncate()

    def run(self):
        print("Searching for latest server weights list...")
        self.ID = self.findid()
        print("Server weight list found!")
        print("ID: " + self.ID)
        print("Retrieving server weights...")
        self.weights = self.findweights()
        # print(self.weights)
        self.updatech()
        print("The server weights are now updated for ch.py, enjoy!")

if __name__ == "__main__":
    updater = Updater()
    updater.run()
