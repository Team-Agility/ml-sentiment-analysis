import sys
sys.setrecursionlimit(2000)

possible_states = ["O","B-positive","I-positive","B-neutral","I-neutral","B-negative","I-negative"]
class Data_processor:
    def __init__(self,path):
        self.datal= []
        self.data = []
        self.file = open(path,'r',encoding="utf8")
        for i in self.file.read().split("\n\n") :
            sentence = []
            unlabeled = []
            for j in i.split("\n"):
                if j != "":
                    unlabeled.append(j)
                    word = j.split(" ")[0].lower()
                    if len(word) > 5 and word[:4] == "http":
                        word = word[:4]
                    if len(j.split(" ")) >1:
                        sentence.append(word + " " +j.split(" ")[-1])
                    else:
                        sentence.append(word)
            if len(sentence) > 0:
                self.data.append(sentence)
                self.datal.append(unlabeled)
        self.file.close()

def emis_prob(a,b,Data,data_dict):
    if (a,b) in data_dict.keys():
        return data_dict[(a,b)]
    else:
        countAB = 0
        countA = 1
        countB = 0
        for tweet in Data.data:
            for j in range(len(tweet)):
                if tweet[j].split(" ")[0] == b:
                    countB +=1
                if tweet[j].split(" ")[1] == a:
                    countA +=1
                    if tweet[j].split(" ")[0] == b:
                        countAB +=1
        if countB == 0:
            result =  float(1/countA)
        else:
            result = float(countAB/countA)
        data_dict[(a,b)] = result
        return result

def trans_prob(a,b,Data,data_dict):
    if (a,b) in data_dict.keys():
        return data_dict[(a,b)]
    else:
        countAB = 0
        countA = 0
        if a == 'start':
            countA = len(Data.data)
            for tweet in Data.data:
                if len(tweet[0].split(" ")) > 1 and tweet[0].split(" ")[1] == b:
                    countAB += 1
        elif b == 'stop':
            for tweet in Data.data:
                for j in range(len(tweet)):
                    if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == a:
                        countA +=1
                        if j == len(tweet)-1:
                            countAB +=1
        elif a == 'stop' or b == 'start':
            data_dict[(a,b)] = 0
            return 0
        else:
            for tweet in Data.data:
                for j in range(len(tweet)-1):
                    if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == a:
                        countA +=1
                        if tweet[j+1].split(" ")[1] == b:
                            countAB +=1
        result = float(countAB/countA)
        data_dict[(a,b)] = result
        return result

# def get_Ysequence(tweet,Data):
#     trans_dict = {}
#     emis_dict = {}
#     score_dict = {}
#     return viterbi_end(tweet,emis_dict,trans_dict,Data,score_dict)

def viterbip5_label(inpathdev,inpathtest,Datapath,os):
    Data = Data_processor(Datapath)
    # Datacount = Data_processor_prepross(Datapath)
    # weight_map = getWeight(Data,50)
    # print ("training done!")
    if os == "W":
        outpathdev = inpathdev.rsplit("\\",maxsplit=1)[0] + "\\dev.p5.out"
        outpathtest = inpathtest.rsplit("\\",maxsplit=1)[0] + "\\test.p5.out"
    else:
        outpathdev = inpathdev.rsplit("/",maxsplit=1)[0] + "/dev.p5.out"
        outpathtest = inpathtest.rsplit("/",maxsplit=1)[0] + "/test.p5.out"
    outfiledev = open(outpathdev,'w',encoding='utf8')
    indatadev = Data_processor(inpathdev)
    # indatadevlabel = Data_processor(inpathdev)
    totaldev = len(indatadev.data)
    transAB_dict = {}
    # transABC_dict = {}
    emis_dict = {}
    for tweet in range(len(indatadev.data)):
        score_dict = {}
        opYseq = viterbiTrigram_end(indatadev.data[tweet],emis_dict,transAB_dict,Data,score_dict)
        for i in range(len(opYseq[0].split(" "))):
            output = indatadev.datal[tweet][i] + " " + opYseq[0].split(" ")[i] + "\n"
            outfiledev.write(output)
        outfiledev.write("\n")
        print("dev " + str(tweet+1)+"/"+str(totaldev)+ " done")
    print("dev done!")
    outfiledev.close()
    outfiletest = open(outpathtest,'w',encoding='utf8')
    indatatest = Data_processor(inpathtest)
    # indatatestlabel = Data_processor(inpathtest)
    totaltest = len(indatatest.data)
    for tweet in range(len(indatatest.data)):
        score_dict = {}
        opYseq = viterbiTrigram_end(indatatest.data[tweet],emis_dict,transAB_dict,Data,score_dict)
        for i in range(len(opYseq[0].split(" "))):
            output = indatatest.datal[tweet][i] + " " + opYseq[0].split(" ")[i] + "\n"
            outfiletest.write(output)
        outfiletest.write("\n")
        print("test "+ str(tweet+1)+"/"+str(totaltest)+ " done")
    print("test done!")
    outfiletest.close()

def viterbi_start(sequence,i,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        score = trans_prob("start",i,Data,trans_dict)*emis_prob(i,sequence[-1],Data,emis_dict)
        score_dict[(len(sequence),i)] = (i,score)
        return (i,score)

def viterbi_end(sequence,emis_dict,trans_dict,Data,score_dict):
    maxY = ""
    maxScore = 0
    for i in possible_states:
        if len(sequence) == 1:
            previous_max = viterbi_start(sequence,i,emis_dict,trans_dict,Data,score_dict)
        else:
            previous_max = viterbiRecursive(sequence,i,emis_dict,trans_dict,Data,score_dict)
        score = previous_max[1]*trans_prob(i,"stop",Data,trans_dict)
        if score > maxScore:
            maxY = previous_max[0]
            maxScore = score
    if maxY == "":
        previous_O = viterbiRecursive(sequence[:-1],"O",emis_dict,trans_dict,Data,score_dict)
        maxY = previous_O[0]
        maxScore = 0
    return (maxY,maxScore)

def viterbiRecursive(sequence,i,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        maxY = ""
        maxScore = 0
        for j in possible_states:
            if len(sequence) == 2:
                previous_max = viterbi_start(sequence[:-1],j,emis_dict,trans_dict,Data,score_dict)
            else:
                previous_max = viterbiRecursive(sequence[:-1],j,emis_dict,trans_dict,Data,score_dict)
            score = previous_max[1]*trans_prob(j,i,Data,trans_dict)*emis_prob(i,sequence[-1],Data,emis_dict)
            if score > maxScore:
                maxY = previous_max[0] + " " + i
                maxScore = score
        if maxY == "":
            previous_O = viterbiRecursive(sequence[:-1],"O",emis_dict,trans_dict,Data,score_dict)
            maxY = previous_O[0] + " " + i
            maxScore = 0
        score_dict[(len(sequence),i)] = (maxY,maxScore)
        return (maxY,maxScore)

EN = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train"
EN_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\dev.in"
EN_in_test = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN_p5\\test.in"
ES = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES\\train"
ES_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES\\dev.in"
ES_in_test = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES_p5\\test.in"
viterbip5_label(EN_in,EN_in_test,EN,"W")
viterbip5_label(ES_in,ES_in_test,ES,"W")