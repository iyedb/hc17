

file = open('in.data', 'r')


class Video(object):
    def __init__(self, vid, size):
        self.vid = vid
        self.size = size
        self.endpoints = {}

    def addendpoint(self, endpoint, reqs):
        if self.endpoints.get(endpoint) is None:
            self.endpoints[endpoint] = reqs
        else:
            self.endpoints[endpoint] += reqs

    def __str__(self):
        s = 'video %d: size %d [' % (self.vid, self.size)
        for k, v in self.endpoints.iteritems():
            s += '(%d, %d)' % (k, v)
        s += ']'
        return s


class Cache(object):
    def __init__(self, cid, size):
        self.cid = cid
        self.size = size
        self.endpoints = {}

    def addendpoint(self, endpoint, latency):
        self.endpoints[endpoint] = latency

    def __str__(self):
        s = 'cache %d [' % self.cid
        for k, v in self.endpoints.iteritems():
            s += '(%d, %d)' % (k, v)
        s += ']'
        return s

    def __eq__(self, other):
        if self.cid == other.cid:
            return True
        return False


def parse(file):
    lines = []
    for line in file:
        if line != '\n':
            lines.append(line)

    vidcount, eps, reqs, ccount, csize = lines[0].split(' ')

    vidcount = int(vidcount)
    eps = int(eps)
    reqs = int(reqs)
    ccount = int(ccount)
    csize = int(csize)

    print 'videos %d' % vidcount
    print 'endpoints %d' % eps
    print 'requests %d' % reqs
    print 'caches %d' % ccount
    print 'cache size %d' % csize

    videos = []
    vids = lines[1].split(' ')
    for vid, size in enumerate(vids):
        videos.append(Video(vid, int(size)))

    for v in videos:
        print v

    line = 2
    endpoints = []
    caches = {}

    for ep in range(eps):
        latencyd, cachecount = lines[line].split(' ')
        latencyd = int(latencyd)
        endpoints.append((ep, latencyd))
        cachecount = int(cachecount)
        for c in range(cachecount):
            line += 1
            cid, latency = lines[line].split(' ')
            cid = int(cid)
            latency = int(latency)
            if caches.get(cid) is None:
                cache = Cache(cid, csize)
                cache.addendpoint(ep, latency)
                caches[cid] = cache
            else:
                caches[cid].addendpoint(ep, latency)

        line += 1

    for k, v in caches.iteritems():
        print v
    
    for i in range(line, len(lines)):
        v, e, r = [int(e) for e in lines[i].split(' ')]
        videos[v].addendpoint(e, r)

    for v in videos:
        print v


parse(file)
