from chat_gpt import ChatGpt


class CaptionFormatter:
    def __init__(self) -> None:
        self.__chatGpt = ChatGpt()
    
    def normalizeStrCaption(self, filePathToStr: str):
        newLines = []
        with open(filePathToStr, 'r') as f:
            lines = f.readlines()
            blockCount = 0
            text = ""
            linesAmount = len(lines)
            for count, line in enumerate(lines):
                blockCount += 1
                if blockCount <= 2:
                    newLines.append(line)
                    continue
                if line == '\n' or linesAmount == count + 1:
                    newLines.append(text.strip())
                    newLines.append('\n\n')
                    text = ""
                    blockCount = 0
                    continue
                
                text += line.replace("\n", " ")                
            
        
        with open(filePathToStr, 'w') as f2:            
            f2.truncate()
            f2.write(''.join(newLines))

                



    def mapCaption(self, filePathToStr: str, maximumCharactersPerTextBlock: int) -> dict:
        '''
        This method have the resposabilty to format the STR formated caption to a dict, mapping the line position
        of the real caption with the line position of the str, because each caption tha is showed in the screen consumes
        three lines of the str file.

        This will also break the text into smaller blocks

        It will return a dict like this:
        {
            "equivalence": 
                {
                    "1": {"startTime": "00:00:002", "endTime": "00:00:002", "strLinePosition": 3, "text": "blalla"}, 
                    "2": {"startTime": "00:00:002", "endTime": "00:00:002", "strLinePosition": 7, "text": "blalla"},
                    "3": {"startTime": "00:00:002", "endTime": "00:00:002", "strLinePosition": 11, "text": "blalla"},
                },
            "textBlocks": [
                ["1", "2"],
                ["3"],
            ]

        The first always going to be 3. The other ones will be the last one plus 4

        '''

        strTextLines: str = ""
        with open(filePathToStr, 'r') as strFile:
            strTextLines = strFile.readlines()

        txtLinePosition = 1
        strLinePosition = 1
        textLineComponents = []
        amountOfCharactersAdded = 0
        map = {
            "equivalence": {},
            "textBlocks": [
                []
            ]
        }
        for strLineText in strTextLines:
            textLineComponents.append(strLineText)

            if  strLinePosition % 4 == 0:
                begin, end = textLineComponents[1].split("-->")
                line = {"startTime": begin.strip(), "endTime": end.strip(),
                        "strLinePosition": strLinePosition - 1, "text": textLineComponents[2]}

                amountOfCharactersAdded += len(line["text"])
                map["equivalence"][txtLinePosition] = line

                if amountOfCharactersAdded <= maximumCharactersPerTextBlock:
                    map["textBlocks"][-1].append(txtLinePosition)
                else:
                    map["textBlocks"].append([txtLinePosition])
                    amountOfCharactersAdded = 0

                txtLinePosition += 1
                textLineComponents.clear()

            strLinePosition += 1

        return map

    def getCuts(self, filePathToStr: str) -> list[dict]:
        self.normalizeStrCaption(filePathToStr=filePathToStr)
        mappedCaption = self.mapCaption(filePathToStr=filePathToStr,
                                        maximumCharactersPerTextBlock=10_000)

        textBlocks: list[list] = mappedCaption["textBlocks"]
        equivalence = mappedCaption["equivalence"]
        print(equivalence)
        cuts = []
        caption = ""
        
        for block in textBlocks:
            if len(block) == 0:
                continue

            globalInitialLine = block[0]
            caption = " ".join([equivalence[line]["text"] for line in block])
            untreatedCuts = self.__chatGpt.requireCuts(captionText=caption)
            try:
                cuts.extend(
                    [
                        {                            
                            "startTime": equivalence[int(untreatedCut["start"]) + globalInitialLine]["startTime"],
                            "endTime": equivalence[int(untreatedCut["end"]) + globalInitialLine]["endTime"],
                            "title": untreatedCut["title"],
                            "resume": untreatedCut["resume"],
                            "quote": untreatedCut["quote"],
                            "selected": False                            
                        } for untreatedCut in untreatedCuts
                    ]
                )
            except Exception as e:
                print(e)
        for i in range(len(cuts)):
            cuts[i]["id"] = i
        return cuts