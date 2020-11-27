import chains
import json
import statistics
import neuralcoref
import spacy

nlp = spacy.load("en_core_web_lg")
neuralcoref.add_to_pipe(nlp)

def parse_test_instance(story):
    """Returns TWO ParsedStory instances representing option 1 and 2"""
    # this is very compressed
    id = story.InputStoryid
    story = list(story)
    sentences = [chains.nlp(sentence) for sentence in story[2:6]]
    alternatives = [story[6], story[7]]
    return [chains.ParsedStory(id, id, chains.nlp(" ".join(story[2:6]+[a])), *(sentences+[chains.nlp(a)])) for a in alternatives]

def story_answer(story):
    """Tells you the correct answer. Return (storyid, index). 1 for the first ending, 2 for the second ending"""
    #obviously you can't use this information until you've chosen your answer!
    return story.InputStoryid, story.AnswerRightEnding

#I wanted to create a function that would compare which dependency pair would give the most information when the choices are given
def dep_info_compare(dependencies,choice):
    res = []
    for dep in dependencies:
        if dep[0] != choice[0]:
            info = table.pmi(dep[0],dep[1],choice[0],choice[1])
            res.append(info)
    return res



# Load training data and build the model
#data, table = chains.process_corpus("train.csv", 100)
#print(table.pmi("move", "nsubj", "move", "nsubj"))

# load the pre-built model
with open("all.json") as fp:
    table = chains.ProbabilityTable(json.load(fp))
'''
Here, I just wanted to check which of the two give out most information.
Looking at the central tendency of each of the two will help determine which gives more information.
This way we will get to choose which one of the two gives the most information and we choose the one with the highest mean (aka average)
'''
# Cloze test

test = chains.load_data("test.csv")
tot = 0
correct = 0


for thingy in test:
    one, two = parse_test_instance(thingy)
    prot1 = chains.protagonist(one)
    prot2 = chains.protagonist(two)
    dep1 = chains.coreferring_pairs(one, prot1[1].root)
    dep2 = chains.coreferring_pairs(two, prot2[1].root)
    choice1 = dep1[-1]    # count from the back
    choice2 = dep2[-1]
    res1 = dep_info_compare(dep1, choice1)
    res2 = dep_info_compare(dep2, choice2)

    # logic to choose between one and two
    # we choose the one with the highest average, therefore we compare which has the highest average

    mean1 = statistics.mean(res1)
    mean2 = statistics.mean(res2)

    if mean1 > mean2:
        res = 1
        print("1 is more informative than 2")
    else:
        res = 2
        print("2 is more informative than 1")

    x = story_answer(thingy)[1]
    if res == x:
        correct +=1
    tot +=1


print(correct + " tests were correct out of " + tot + "tests.")
print( "Accuracy = " + (correct/tot)*100 + "%")