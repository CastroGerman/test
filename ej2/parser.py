import pathlib
import re

MEM_FILE_NAME = "memVal.mem"
GEN_FILE_NAME = "generated.v"

def getMemValues(file):
    rv = []
    pattern = re.compile(r'  reg \[(.*)\] (\S*) \[(.*)\];\n  initial begin\n((    \S*\[\S*\] = \S*;\n)*)  end\n')
    memValPat = re.compile(r'\S\'h(\S*);')
    with open(file, 'r') as f:
        for match in re.finditer(pattern, f.read()):           
            for match2 in re.finditer(memValPat, match.group(4)):
                rv.append(match2.group(1))       
    return rv   

def generateMemFile(dest, source):
    valsToWirte = []
    for vals in getMemValues(source):
        valsToWirte.append(vals+"\n")
    with open(dest, 'w') as f:
        f.writelines(valsToWirte)
        
def generateVFile(dest, memSource, vSource):
    linesToWrite = []
    pattern = re.compile(r'  reg \[(.*)\] (\S*) \[(.*)\];\n  initial begin\n((    \S*\[\S*\] = \S*;\n)*)  end\n')
    
    with open(vSource, 'r') as f:
        knownChunks = pattern.split(f.read())
        
    linesToWrite.append(knownChunks[0])
    linesToWrite.append("  reg [{}] {} [{}];\n".format(knownChunks[1], knownChunks[2], knownChunks[3]))
    linesToWrite.append("  $readmemh(\"{}\", {});\n".format(memSource, knownChunks[2]))
    linesToWrite.append(knownChunks[-1])

    with open(dest, 'w') as gf:
        gf.writelines(linesToWrite)

def parser(destFolder, sourceFile):
    pathlib.Path(destFolder).mkdir(exist_ok=True)  
    memValFilePath = pathlib.Path(destFolder).joinpath(MEM_FILE_NAME)
    genFilePath = pathlib.Path(destFolder).joinpath(GEN_FILE_NAME)

    generateMemFile(memValFilePath, sourceFile)
    generateVFile(genFilePath, memValFilePath.relative_to(destFolder), sourceFile)


if __name__ == '__main__':

    sourceFilePath = "testcase.v"
    destFolderPath = "generated"
    parser(destFolderPath, sourceFilePath)