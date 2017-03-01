import sys
import numpy as np
from scipy.spatial import distance





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

    def to_vec(self, length):
        arr = np.zeros(length, dtype=np.int32)
        for k, v in self.endpoints.iteritems():
            arr[k] = 1
        return arr

    def popularity(self):
        acc = 0
        for k, v in self.endpoints.iteritems():
            acc += v
        return acc


    def __cmp__(self, other):
        return self.popularity() - other.popularity()

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
        self.videos = []

    def addendpoint(self, endpoint, latency):
        self.endpoints[endpoint] = latency

    def put(self, video):
        if self.size >= video.size:
            self.size -= video.size
            self.videos.append(video)
            return True
        return False

    def to_vec(self, length):
        arr = np.zeros(length, dtype=np.int32)
        for k, v in self.endpoints.iteritems():
            arr[k] = v
        return arr

    def dist(self, baselength):
        return distance.euclidean(self.to_vec(baselength), np.zeros(baselength, dtype=np.int32))

    def videolist(self):
        return [v.vid for v in self.videos]

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

    def __cmp__(self, other):
        return self.popularity() - other.popularity()


def parse(file):
    lines = []
    for line in file:
        if line != '\n':
            lines.append(line)

    vidcount, eps, reqs, ccount, csize = [int(e) for e in lines[0].split(' ')]

    # print 'videos %d' % vidcount
    # print 'endpoints %d' % eps
    # print 'requests %d' % reqs
    # print 'caches %d' % ccount
    # print 'cache size %d' % csize

    videos = []
    vids = lines[1].split(' ')
    for vid, size in enumerate(vids):
        videos.append(Video(vid, int(size)))

    # for v in videos:
    #    print v

    line = 2
    endpoints = []
    caches = {}
    reqs = {}

    for ep in range(eps):
        latencyd, cachecount = [int(e) for e in lines[line].split(' ')]
        endpoints.append((ep, latencyd))
        for c in range(cachecount):
            line += 1
            cid, latency = [int(e) for e in lines[line].split(' ')]
            if caches.get(cid) is None:
                cache = Cache(cid, csize)
                cache.addendpoint(ep, latency)
                caches[cid] = cache
            else:
                caches[cid].addendpoint(ep, latency)

        line += 1

    for i in range(line, len(lines)):
        v, e, r = [int(e) for e in lines[i].split(' ')]
        videos[v].addendpoint(e, r)


    return [v for v in videos if v.popularity() != 0], caches, endpoints




# for k, v in caches.iteritems():
#     print v.cid, v.videolist()

if __name__ == '__main__':

    file = open(sys.argv[1], 'r')
    out = sys.argv[1].split('.')[0]
    out = out + '.out'
    print out
    videos, caches, eps = parse(file)

    # for k, v in caches.iteritems():
    #     print 'cache %d vector:' % v.cid, v.to_vec(len(eps)), v.dist(len(eps))

    videos = sorted(videos, reverse=True)

    """
    for v in videos:
        print 'video %d vector:' % v.vid, v.to_vec(len(eps)),\
                ' %s' % v.popularity()
    """

    for video in videos:
        # print 'Video %d =>' % video.vid
        distances = []
        for k, v in caches.iteritems():
            d = distance.cosine(v.to_vec(len(eps)), video.to_vec(len(eps)))
            distances.append((v.cid, d, v.dist(len(eps)), v.size))
            # print 'D(video %d, cache %d)' % (video.vid, v.cid), d
        # print 'video %d:' % video.vid, sorted(distances, key=lambda x: (x[1], x[2]))
        distances = sorted(distances, key=lambda x: (x[1], x[2]))
        for e in distances:
            if e[1] == 1.0:
                continue
            cache_ = caches.get(e[0])
            if cache_.put(video):
                break

        # print '----'
    sol = open(out, 'w')
    numcaches = 0
    outcaches = []
    for k, v in caches.iteritems():
        if len(v.videolist()):
            numcaches += 1
            outcaches.append(v)
    outcaches = sorted(outcaches, key=lambda x: x.cid)
    sol.write('%d\n' % numcaches)

    for c in outcaches:
        sol.write('%d ' % c.cid)
        for v in c.videolist():
            sol.write('%d ' % v)
        sol.write('\n')

