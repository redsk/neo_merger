import sys


class MatchKBs():
    def __init__(self, WNnodesFilename, WNedgesFilename, CNnodesFilename, CNedgesFilename, matchedNodesFilename, matchedEdgesFilename):
        self.WNnodesFilename = WNnodesFilename
        self.WNedgesFilename = WNedgesFilename
        self.CNnodesFilename = CNnodesFilename
        self.CNedgesFilename = CNedgesFilename
        self.matchedNodesFilename = matchedNodesFilename
        self.matchedEdgesFilename = matchedEdgesFilename

    def matchKBs(self):
        print 'Reading WordNet nodes and edges...',
        sys.stdout.flush()
        self.WNnodesList, self.WNnodesFields, self.WNnodesTypes = self.readCSV(self.WNnodesFilename)
        self.WNrelsList, self.WNrelsFields, self.WNrelsTypes = self.readCSV(self.WNedgesFilename)
        print 'done.'

        print 'Reading ConceptNet nodes and edges...',
        sys.stdout.flush()
        self.CNnodesList, self.CNnodesFields, self.CNnodesTypes = self.readCSV(self.CNnodesFilename)
        self.CNrelsList, self.CNrelsFields, self.CNrelsTypes = self.readCSV(self.CNedgesFilename)
        print 'done.'

        print 'Creating data structures...',
        sys.stdout.flush()
        self.wn = OrderedDictionary(self.getDictFromListOfNodes(self.WNnodesList))
        self.cn = OrderedDictionary(self.getDictFromListOfNodes(self.CNnodesList))
        print 'done.'

        print 'Writing merged Nodes File...',
        sys.stdout.flush()
        self.writeCSV( self.matchedNodesFilename, 
                       [self.WNnodesList, self.CNnodesList], \
                       [self.WNnodesFields, self.CNnodesFields], \
                       [self.WNnodesTypes, self.CNnodesTypes] )
        print 'done.'

        print 'Matching nodes...',
        sys.stdout.flush()
        self.matchNodes()
        print 'done.'

        print 'Writing merged Edges File...',
        sys.stdout.flush()
        self.writeCSV( self.matchedEdgesFilename, \
                       [self.WNrelsList, self.CNrelsList, self.matchedRels], \
                       [self.WNrelsFields, self.CNrelsFields], \
                       [self.WNrelsTypes, self.CNrelsTypes] )
        print 'done.'



    def readCSV(self, filename):
        lines = None
        with open(filename, 'r') as f:
            lines = f.readlines()

        fields = lines[0][:-1].split('\t') # [:-1] to remove '\n'
        types = []
        for f in fields:
            t = ''
            Scolon = f.split(':')
            if len(Scolon) > 1:
                if Scolon[1] == 'int':
                    t = 'i'
                elif Scolon[1] == 'float':
                    t = 'f'
            else:
                t = 's' # string
            if '[]' in f:
                t = t + 'a' # array of 
            # override for 'id:ID' and ':LABEL'
            if f in ['id:ID', ':LABEL', ':START_ID', ':END_ID',  ':TYPE']:
                t = 's'
            types.append(t)
        
        l = []
        for i in range(1, len(lines)):
            values = lines[i][:-1].split('\t') # [:-1] to remove '\n'
            name = values[0][1:-1] # removing ""

            # if name.startswith('wn/'):
            #     name = name[3:]

            n = {} 
            for j in range(0, len(values)):
                if values[j] != '' and values[j] != '""':   # in that case, the value is null for that record
                    if types[j] == 'i':
                        n[fields[j]] = int(values[j])
                    elif types[j] == 'f':
                        n[fields[j]] = float(values[j])
                    elif types[j] == 's':
                        if values[j][0] == '"' and values[j][-1] == '"':
                            n[fields[j]] = values[j][1:-1] # removing ""
                        else:
                            n[fields[j]] = values[j] # Labels might have no ""...
                    elif types[j] == 'ia':
                        n[fields[j]] = [int(i) for i in values[j].split(';')]
                    elif types[j] == 'fa':
                        n[fields[j]] = [float(i) for i in values[j].split(';')]
                    elif types[j] == 'sa':
                        n[fields[j]] = values[j][1:-1].split(';')
            l.append(n)
        return l, fields, types


    def getDictFromListOfNodes(self, l):
        d = {}
        for e in l:
            d[ e['id:ID'] ] = e
        return d


    def writeCSV(self, filename, ItemsLists, ItemFields, ItemsTypes):
        matchedFields, matchedTypes = self.matchHeaders(ItemFields, ItemsTypes)

        with open(filename, 'w') as of:
            header = '\t'.join(matchedFields)
            of.write(header + '\n')

            for l in ItemsLists:
                for i in l:
                    line = ''
                    for idx, f in enumerate(matchedFields):
                        if f in i:
                            if matchedTypes[idx] in ['i', 'f']:
                                line += str(i[f])
                                #of.write(str(i[f]))
                            elif matchedTypes[idx] == 's':
                                line += '"{0}"'.format(i[f]) 
                                # of.write( '"{0}"'.format(i[f]) )
                            elif matchedTypes[idx] in ['ia', 'fa']:
                                line += '"{0}"'.format( ';'.join([str(j) for j in i[f]]) ) 
                                # of.write( '"{0}"'.format( ';'.join([str(j) for j in i[f]]) ) )
                            elif matchedTypes[idx] == 'sa':
                                line += '"{0}"'.format( ';'.join(i[f]) ) 
                                # of.write( '"{0}"'.format( ';'.join(i[f]) ) )
                        line += '\t'
                        #of.write('\t')
                    of.write( line[:-1] + '\n' ) # line[:-1] because there's an extra tab at the end
                    # of.write('\n')



    def matchHeaders(self, FieldsList, TypesList):
        matchedFields = []
        matchedTypes = []
        for idxFL, fl in enumerate(FieldsList):
            for idxF, f in enumerate(fl):
                if f not in matchedFields:
                    matchedFields.append(f)
                    matchedTypes.append( TypesList[idxFL][idxF] )
        return matchedFields, matchedTypes

    def addRel(self, c, w):
        self.matchedRels.append( {':START_ID': c, ':END_ID': w, ':TYPE': 'KBmatch'} )


    def matchNodes(self):
        self.matchedRels = []

        matched = 0
        multiple_matched = 0
        for idx, c in enumerate(self.cn.nd):
            t = c[6:].replace('_', '+').split('/')
            if len(t) > 1:
                w = 'wn/' + t[0] + '-' + t[1]
                if t[1] == 'a':
                    if w not in self.wn.nd:
                        w = w[:-1] + 's'
                if w in self.wn.nd:
                    matched += 1
                    self.addRel(c, w)
            else:
                w = 'wn/' + t[0]
                if w in self.wn.nd:
                    matched += 1
                    self.addRel(c, w)
                else:
                    mf = False
                    for pos in ['n', 'v', 'a', 'r', 's']:
                        s = w + '-' + pos
                        if s in self.wn.nd:
                            matched += 1
                            self.addRel(c, s)
                            if mf == False:
                                mf = True
                            else:
                                multiple_matched += 1
                    
            if idx % 100000 == 0:
                print '.',
                sys.stdout.flush()
        print matched, multiple_matched


class OrderedDictionary():
    def __init__(self, dictionary):
        self.nd = dictionary
        self.n = sorted(self.nd.keys())
        self.d = {}
        for i in range(0, len(self.n)):
            self.d[ self.n[i] ] = i
            
    def __getitem__(self, indexOrString):
        if type(indexOrString) is str:
            return self.nd[indexOrString]
        elif type(indexOrString) is int:
            return self.nd[ self.n[indexOrString] ]
        else:
            errorMessage = self.__class__.__name__ + 'indices must be integers or strings, not ' + str(type(indexOrString))
            raise TypeError(errorMessage)
    
    def pos(self, element):
        return self.d[element]
    
    def next(self, element):
        p = self.d[element]
        if p + 1 < len(self.n):
            return self.nd[ self.n[p + 1] ]
        return None
    
    def sameRoot(self, element):
        res = []
        root = element.split('#')[0]
        rootNode = self.nd[root]
        idx = self.d[root]
        while True:
            res.append(self.nd[ self.n[idx] ])
            idx += 1
            if idx < len(self.n):
                node = self.nd[ self.n[idx] ]
                rootName = node['id:ID'].split('#')[0]
                if rootName != root:
                    break
            else:
                break
        return res


def main():
    m = None
    numargs = len(sys.argv)
    if numargs == 1:
        m = MatchKBs('wordnet/WNnodes.csv', 'wordnet/WNedges.csv', 'conceptnet/nodes.csv', 'conceptnet/edgesPOS.csv', 'merged-kbs/nodes.csv', 'merged-kbs/edges.csv')
    if numargs == 7:
        m = MatchKBs(*sys.argv[1:])
    if numargs != 1 and numargs != 7:
        print "Usage:\npython neo_merger.py <wordnet nodes> <wordnet edges> <conceptnet nodes> <conceptnet edges> <output nodes> <output edges>\n"
    else:
        m.matchKBs()

if __name__ == "__main__":
    main()


