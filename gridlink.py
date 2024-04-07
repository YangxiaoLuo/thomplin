from random import randint
from gridlink_data import *

class Gridlink:
    def __init__(self, gridlist, moves=[]):
        self.gridlist = gridlist
        self.moves = moves
        self.components = len(gridlist)
        self.segments = []
        self.set_size(self.gridlist)
        self.build(self.gridlist)
        
    def set_size(self, gridlist):
        self.size = 0
        for component in gridlist:
            self.size += len(component)/2
        self.size = int(self.size)
        self.hlist = [None for i in range(self.size)]
        self.vlist = [None for i in range(self.size)]
        
    def build(self, gridlist):
        for component in gridlist:
            horizontal = True
            seglist = []
            for i in component:
                newsegment = Segment(i, horizontal)
                seglist.append(newsegment)
                if horizontal:
                    self.hlist[i] = newsegment
                else:
                    self.vlist[i] = newsegment
                horizontal ^= True
            for i in range(len(seglist)):
                seglist[i-1].connect(seglist[i])
            self.segments += seglist
            
    def exchange(self, i, type, record=True):
        if type == 'h':
            seglist = self.hlist
        elif type == 'v':
            seglist = self.vlist
        else:
            pass
        i = i % self.size
        j = (i+1) % self.size
        if self.legal(seglist[i], seglist[j]):
            temp = seglist[i]
            seglist[i] = seglist[j]
            seglist[j] = temp
            seglist[i].level = i
            seglist[j].level = j
            if record:
                self.moves.append(('exchange',type,i))
            else:
                pass
        else:
            pass

    def legal(self, seg1, seg2):
        u0, u1 = seg1.prev.level, seg1.next.level
        v0, v1 = seg2.prev.level, seg2.next.level
        if min(u0,u1) < min(v0,v1) < max(u0,u1) < max(v0,v1):
            return 0
        if min(v0,v1) < min(u0,u1) < max(v0,v1) < max(u0,u1):
            return 0
        return 1

    def roll(self, h, v, record=True):
        h = int(h % self.size)
        v = int(v % self.size)
        self.hlist = self.hlist[h:]+self.hlist[:h]
        self.vlist = self.vlist[v:]+self.vlist[:v]
        for i in range(self.size):
            self.hlist[i].level = i
            self.vlist[i].level = i
        if record:
            self.moves.append(('roll',h,v))
        else:
            pass
            
    def reverse_component(self, segment):
        next = segment.next
        segment.reverse()
        while next != segment:
           next.reverse()
           next = next.prev

    def reflect(self):
        for seg in self.hlist + self.vlist:
            seg.reflect(self.size)
        self.hlist, self.vlist = self.vlist, self.hlist
        self.vlist.reverse()
        
    Opposite = {'E':'W', 'W':'E', 'N':'S', 'S':'N' }

    def destab_type(self, segment):
        if len(segment) != 1:
            return
        if segment.horizontal:
            dir = Gridlink.Opposite[segment.dir()]
            next_dir = segment.next.dir()
            if (segment.next.dir() != segment.prev.dir() and
                len(segment.next) > len(segment.prev)):
                next_dir = Gridlink.Opposite[next_dir]
            return next_dir + dir
        else:
            dir = segment.dir()
            next_dir = Gridlink.Opposite[segment.next.dir()]
            if (segment.next.dir() != segment.prev.dir() and
                len(segment.next) > len(segment.prev)):
                next_dir = Gridlink.Opposite[next_dir]
            return dir + next_dir

    Hshift = {'NW':0, 'NE':0, 'SW':1 , 'SE':1 }

    Vshift = {'NW':0, 'NE':1, 'SW':0 , 'SE':1 }
    
    def stabilize(self, segment, type, record=True):
        index = segment.level
        self.size += 1
        V = Segment(0, False)
        H = Segment(0, True)
        self.segments += [V,H]
        hs = Gridlink.Hshift[type]
        vs = Gridlink.Vshift[type]
        if segment.horizontal:
            segtype = 'h'
            H.connect(V)
            self.hlist.insert(segment.level + 1 - hs, H)
            self.vlist.insert(segment.prev.level + 1 - vs, V)
            segment.prev.connect(H)
            V.connect(segment)
        else:
            segtype = 'v'
            V.connect(H)
            self.hlist.insert(segment.prev.level + hs, H)
            self.vlist.insert(segment.level + vs, V)
            segment.prev.connect(V)
            H.connect(segment)
        for i in range(self.size):
            self.hlist[i].level = i
            self.vlist[i].level = i
        if record:
            self.moves.append(('stabilize', segtype, index, type)) 

    def destabilize(self, segment, record=True):
        type = self.destab_type(segment)
        sign = 1
        if len(segment) == 1 and segment.next.next != segment.prev.prev:
            seg = segment
            if  segment.prev.dir() == segment.next.dir():
                adjacent = segment.next
                remember = adjacent.next
                if adjacent.dir() in ('E','S'):
                    sign = -1
                seg.prev.next = adjacent.next
                adjacent.next.prev = seg.prev
            else:
                if len(segment.next) < len(segment.prev):
                    adjacent = segment.next
                    remember = adjacent.next
                    if adjacent.dir() in ('E','S'):
                        sign = -1
                    seg.prev.next = adjacent.next
                    adjacent.next.prev = seg.prev
                else:
                    adjacent = segment.prev
                    remember = segment.next
                    if adjacent.dir() in ('W','N'):
                        sign = -1
                    adjacent.prev.next = seg.next
                    seg.next.prev = adjacent.prev
            count = sign*(len(adjacent) - 1)
            exchanges = (segment.level - count, count)
            if segment.horizontal:
                exchanges = ('h',) + exchanges
            else:
                exchanges = ('v',) + exchanges
            index = remember.level
            seg.next = seg.prev = adjacent.next = adjacent.prev = None
            if seg.horizontal:
                self.hlist.remove(seg)
                self.vlist.remove(adjacent)
            else:
                self.hlist.remove(adjacent)
                self.vlist.remove(seg)
            self.segments.remove(seg)
            self.segments.remove(adjacent)
            self.size -= 1
            for i in range(self.size):
                self.hlist[i].level = i
                self.vlist[i].level = i
            if record:
                if remember.horizontal:
                    segtype = 'h'
                else:
                    segtype = 'v'
                self.moves.append(
                    ('destabilize', segtype, index, type, exchanges))
            return True
        return False

    def destabilize_any(self, excluded=[]):
        for list in (self.hlist, self.vlist):
            for segment in list:
                if self.destab_type(segment) in excluded:
                    continue
                if self.destabilize(segment):
                    return True
        return False
            
    def inverse(self, move):
        op = move[0]
        if op == 'roll':
            h,v = move[1:3]
            self.roll(-h, -v, record=False)
        segtype, index = move[1:3]
        if op == 'exchange':
            self.exchange(index, segtype, record=False)
        if op == 'stabilize':
            type = move[3]
            if segtype == 'h':
                segment = self.hlist[index+Gridlink.Hshift[type]]
            else:
                segment = self.vlist[index-Gridlink.Vshift[type]+1]
            self.destabilize(segment.prev, record=False)
        if op == 'destabilize':
            type, exchanges = move[3:5]
            if segtype == 'h':
                segment = self.hlist[index-Gridlink.Hshift[type]]
            else:
                segment = self.vlist[index+Gridlink.Vshift[type]-1]
            save = segment.prev
            self.stabilize(segment, type, record=False)
            segtype, index, count = exchanges
            if count > 0:
                for i in range(count):
                    self.exchange(index + i, segtype, record=False) 
            else:
                for i in range(-count):
                    self.exchange(index - i - 1, segtype, record=False)

    def apply(self, move):
        op = move[0]
        if op == 'roll':
            h,v = move[1:3]
            self.roll(h, v, record=False)
        segtype, index = move[1:3]
        if op == 'exchange':
            self.exchange(index, segtype, record=False)
        if op == 'stabilize':
            type = move[3]
            if segtype == 'h':
                segment = self.hlist[index]
            else:
                segment = self.vlist[index]
            self.stabilize(segment, type, record=False)
        if op == 'destabilize':
            type, exchanges = move[3:5]
            segtype, index, count = exchanges
            if segtype == 'h':
                segment = self.hlist[index + count]
            else:
                segment = self.vlist[index + count]
            self.destabilize(segment, record=False)

    def undo(self):
        move = self.moves.pop()
        self.inverse(move)

    def randomize(self, n=1):
        self.moves=[]
        while n > 0:
            if randint(0,1):
                dir = 'h'
            else:
                dir = 'v'
            if randint(0,1):
                strand = randint(0,self.size)
                self.exchange(strand, dir, record=False)
            else:
                j, k = randint(0, self.size-1), randint(0, self.size-1)
                self.roll(j, k, record=False)
            n -= 1

    def randomize2(self, n=1):
        """
        Experimental version that tries a few stabilizations.
        """
        self.moves=[]
        while n > 0:
            if randint(0,1):
                dir = 'h'
            else:
                dir = 'v'
            move = randint(0,5)
            if move < 2:
                strand = randint(0,self.size)
                self.exchange(strand, dir, record=False)
            elif move < 4:
                j, k = randint(0, self.size), randint(0, self.size)
                self.roll(j, k, record=False)
            else:
                type = ('NW','NE','SW','SE')[randint(0,3)]
                seg = randint(0, self.size)
                self.stabilize(self.hlist[randint(0,self.size-1)],
                               type, record=False)
            n -= 1

    def simplify(self, iterates=10000, lower_bound=5):
        excluded = []
        while iterates:
            iterates -= 1
            self.randomize()
            self.destabilize_any(excluded)
            if self.size < lower_bound:
                break
            # while self.destabilize_any(excluded):
            #     pass
    
    def legendrian_simplify(self, iterates=10000):
        excluded = []
        while iterates:
            iterates -= 1
            self.randomize()
            self.destabilize_any(['NE', 'SW'])
            
    def print_moves(self):
        for move in self.moves:
            print ('\t'.join([str(x) for x in move]))

    def get_gridlist(self):
        gridlist = []
        H = [segment for segment in self.hlist]
        V = [segment for segment in self.vlist]
        while len(H) > 0:
            nexth = first = H[0]
            component = []
            while True:
                component.append(nexth.level)
                H.remove(nexth)
                nextv = nexth.next
                component.append(nextv.level)
                nexth = nextv.next
                if nexth == first:
                    break
            gridlist.append(component)
        return gridlist

    def get_XOlists(self):
        """
        Return lists X and O.
        X[i] (O[i]) is the y coordinate of the X (O) vertex in column i.
        THE BOTTOM OF THE DIAGRAM HAS Y-COORDINATE 0.
        """
        X = []
        O = []
        for segment in self.vlist:
            X.append(self.size - 1 - segment.prev.level)
            O.append(self.size - 1 - segment.next.level)
        return X, O
    
    # def HFKhat(self):
    #     if self.components > 1:
    #         showwarning('Knots only',
    #                     'Sorry, I can only compute HFK^ for knots.')
    #         return
    #     Xlist, Olist = self.get_XOlists(force_zero=True)
    #     hfk_object = TkHFK(Xlist, Olist, name=self.window.title())
    #     hfk_object.HFK_ranks()

    def winding_numbers(self):
        result = []
        for i in range(self.size):
            row = [0]
            for j in range(self.size):
                tail = self.vlist[j].prev.level
                head = self.vlist[j].next.level
                if tail <= i < head:
                    row.append(row[-1] + 1)
                elif head <= i < tail:
                    row.append(row[-1] - 1)
                else:
                    row.append(row[-1])
            result.append(row)
        return result

    def Alexander_shift(self):
        """
        This follows the convention used by Baldwin and Gillam.
        """
        X = [seg.next.level for seg in self.vlist]
        O = [seg.prev.level for seg in self.vlist]
        X.append(X[0])
        O.append(O[0])
        WN = self.winding_numbers()
        for row in WN:
            row.append(row[0])
        S = 0
        for i in range(self.size):
            S += WN[X[i]][i]
            S += WN[X[i]-1][i];
            S += WN[X[i]][i+1];
            S += WN[X[i]-1][i+1];
            S += WN[O[i]][i]
            S += WN[O[i]-1][i];
            S += WN[O[i]][i+1];
            S += WN[O[i]-1][i+1];
        shift = (S - 4 * self.size + 4)/8;
        return shift

    def writhe(self):
        """
        Compute the writhe of the diagram.
        """
        positive = 0
        negative = 0
        for V in self.vlist:
            for H in self.hlist:
                #down
                if V.prev.level < H.level < V.next.level:
                    if H.prev.level < V.level < H.next.level:
                        positive += 1
                    elif H.prev.level > V.level > H.next.level:
                        negative += 1
                #up
                if V.prev.level > H.level > V.next.level:
                    if H.prev.level < V.level < H.next.level:
                        negative += 1
                    elif H.prev.level > V.level > H.next.level:
                        positive += 1
        return positive - negative

    def rotation(self):
        """
        Compute the rotation number of the diagram.
        """
        r = 0
        for V in self.vlist:
            if V.prev.dir() == 'W' and V.dir() == 'S': r += 1
            if V.dir() == 'S' and V.next.dir() == 'W': r += 1
            if V.prev.dir() == 'E' and V.dir() == 'N': r -= 1
            if V.dir() == 'N' and V.next.dir() == 'E': r -= 1
        return r/2

    def tb(self):
        """
        Compute the Thurston-Bennequin number of the diagram.
        """
        northeast = 0
        for V in self.vlist:
            if ((V.dir() == 'N' and V.next.dir() == 'W') or
                (V.dir() == 'S' and V.prev.dir() == 'E')):
                    northeast += 1
        return -self.writhe() - northeast
                
class Segment:

    def __init__(self, level, horizontal):
        self.level = level
        self.horizontal = horizontal
        self.next = None
        self.prev = None

    def __len__(self):
        return abs(self.next.level - self.prev.level)

    def dir(self):
        if self.horizontal:
            if self.prev.level < self.next.level:
                return 'E'
            else:
                return 'W'
        else:
            if self.prev.level < self.next.level:
                return 'S'
            else:
                return 'N'
            
    def connect(self, other):
        self.next = other
        other.prev = self

    def reverse(self):
        save = self.next
        self.next = self.prev
        self.prev = save
        
    def reflect(self, size):
        if self.horizontal:
            self.level = size - self.level - 1
        self.horizontal ^= 1
        
class Unknot(Gridlink):
    """
    An unknot on an nxn grid.  Instantiate as Unknot(n).
    """
    
    def __init__(self, n):
        gridlist = range(2*n)
        for i in gridlist:
            gridlist[i] = i/2
        Gridlink.__init__(self, [gridlist])
        
    def __repr__(self):
       return 'unknot of size %d'%self.size

class ClosedBraid(Gridlink):
    """
    A gridlink representation of a closed braid.
    """
    def __init__(self, strands, word=None):
        self.strands = strands
        self.matrix = [[1]*self.strands]
        self.indices = range(self.strands)
        self.size = self.strands
        if word:
            for x in word:
                self.twist(x)
        self.close()
        Gridlink.__init__(self, self.braid_to_gridlist())

    def __repr__(self):
        return self.diagram()
    
    def diagram(self):
        result = ''
        for row in self.matrix:
            for entry in row:
                if entry:
                    result += '*'
                else:
                    result += '.'
            result += '\n'
        return result

    def twist(self, k):
        """
        Switch strands |k|-1 and |k|.
        Positive sign means to cross strand k over strand k-1.
        Strands are numbered from 0.
        """
        if k == 0 or abs(k) >= self.strands:
            raise ValueError('Invalid strand index')
        if k < 0:
            k = -k
            self.size += 1
            for row in self.matrix:
                row.insert(self.indices[k-1],0)
            self.matrix.append([0]*self.size)
            self.matrix[-1][self.indices[k]+1] = 1
            for i in range(k+1, self.strands):
                self.indices[i] += 1
            self.indices[k] = self.indices[k-1] + 1
            self.matrix[-1][self.indices[k-1]] = 1
        elif k > 0:
            self.size += 1
            for row in self.matrix:
                row.insert(self.indices[k]+1,0)
            self.matrix.append([0]*self.size)
            self.matrix[-1][self.indices[k-1]] = 1
            self.indices[k-1] = self.indices[k]
            for i in range(k,self.strands):
                self.indices[i] += 1
            self.matrix[-1][self.indices[k]] = 1

    def close(self):
        start = self.matrix.pop(0)
        n = start.index(1)
        bottom = [[0]*self.size for i in range(self.strands)]

        #connect each non-trivial strand back to its start
        j = k = 0
        for i in range(self.strands):
            j = len([x for x in self.indices[i+1:] if x < n]) 
            bottom[k+j][n] = 1
            bottom[k+j][self.indices[i]] = 1
            if j == 0:
                k = i+1
            try:
                n = start.index(1,n+1)
            except ValueError:
                break
        self.matrix += bottom
        # Now deal with the trivial strands
        k = 0
        while k < self.size:
            if 1 == sum([self.matrix[j][k] for j in range(self.size)]):
                for row in self.matrix:
                    row.insert(k,0)
                self.size += 1
                self.matrix[k][k] = 1
                self.matrix.insert(0,[0]*self.size)
                self.matrix[0][k] = 1
                self.matrix[0][k+1] = 1
                for i in range(k,self.strands):
                    self.indices[i] += 1
                k += 2
            else:
                k += 1
        
    def braid_to_gridlist(self):
        dots = []
        gridlist = []
        for row in self.matrix:
            first = row.index(1)
            second = row.index(1, first+1)
            dots.append([first, second])
        while True:
            index = -1
            component = []
            for dot in dots:
                if dot:
                    index = dots.index(dot)
                    break
            if index == -1:
                break
            dot = dots[index]
            while True:
                if not dot:
                    break
                x = dot.pop()
                component.append(index)
                component.append(x)
                for next in dots:
                   if x in next:
                       index = dots.index(next)
                       next.remove(x)
                       dot = next
                       break
            gridlist.append(component)
        return gridlist

Bad_Knot_name = 'Example knot names:  9_12 11a_123 12n_1123'

class Knot(ClosedBraid):
    """
    A gridlink representation of a knot with up to 12 crossings.
    The knot name should look like 9_12 or 11n_123 or 12a_123.
    """
    def __init__(self, name):
        try:
            braid = knot_dict[name]
        except:
            raise Bad_Knot_name 
        strands = max([abs(x) for x in braid]) + 1
        ClosedBraid.__init__(self, strands, braid)

class XOlink(Gridlink):
    """
    A gridlink representation specified by a matrix with one X and one O
    in each row and column.  Vertical segments are oriented from X to O,
    horizontal segments from O to X.  Initialize with two lists, one
    containing the row indices of X's, the other containing row indices
    of the O's.  THE ROWS ARE ORDERED BOTTOM TO TOP.
    """
    def __init__(self, Xlist, Olist):
        gridlist = []
        size = len(Xlist)
        rows = [*range(size)]
        while len(rows) > 0:
            O = rows.pop(0)
            component = [size - 1 - O]
            while True:
                X = Xlist.index(O)
                component.append(X)
                O = Olist[X]
                if O not in rows:
                    break
                component.append(size - 1 - O)
                rows.remove(O)
            gridlist.append(component)
        Gridlink.__init__(self, gridlist)