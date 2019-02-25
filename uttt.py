from time import sleep
from math import inf
from random import randint
from copy import deepcopy
from collections import Counter
import sys
import time

class ultimateTicTacToe:

    board_axis = [
        #rows
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],

        #cols
        [(0,0),(1,0),(2,0)],
        [(0,1),(1,1),(2,1)],
        [(0,2),(1,2),(2,2)],

        #diagonals
        [(0,0),(1,1),(2,2)],
        [(0,2),(1,1),(2,0)]]

    board_corners = [
        (0,0),(0,2),(0,3),(0,5),(0,6),(0,8),
        (2,0),(2,2),(2,3),(2,5),(2,6),(2,8),
        (3,0),(3,2),(3,3),(3,5),(3,6),(3,8),
        (5,0),(5,2),(5,3),(5,5),(5,6),(5,8),
        (6,0),(6,2),(6,3),(6,5),(6,6),(6,8),
        (8,0),(8,2),(8,3),(8,5),(8,6),(8,8)]
    
    axis_max_win = 27
    axis_min_win = 8

    axis_max_pot = 9
    axis_min_pot = 4

    axis_max_block = 12
    axis_min_block = 18

    axis_max_solo = 3
    axis_min_solo = 2

    axis_empty = 1

    axis_not_max_only = set([axis_max_win,axis_min_win,axis_max_pot,axis_min_pot,axis_max_block,axis_min_block,axis_min_solo,axis_empty])
    axis_not_min_only = set([axis_max_win,axis_min_win,axis_max_pot,axis_min_pot,axis_max_block,axis_min_block,axis_max_solo,axis_empty])

    def __init__(self):
        """
        Initialization of the game.
        """
        self.board=[['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_']]
        self.maxPlayer='X'
        self.minPlayer='O'
        self.maxDepth=3
        #The start indexes of each local board
        self.globalIdx=[(0,0),(0,3),(0,6),(3,0),(3,3),(3,6),(6,0),(6,3),(6,6)]
        #Start local board index for reflex agent playing
        self.startBoardIdx=4
        #self.startBoardIdx=randint(0,8)


        self.currBoardIdx=self.startBoardIdx

        #utility value for reflex offensive and reflex defensive agents
        self.winnerMaxUtility=10000
        self.twoInARowMaxUtility=500
        self.preventThreeInARowMaxUtility=100
        self.cornerMaxUtility=30

        self.winnerMinUtility=-10000
        self.twoInARowMinUtility=-100
        self.preventThreeInARowMinUtility=-500
        self.cornerMinUtility=-30

        self.expandedNodes=0
        self.currPlayer=True

    def printGameBoard(self):
        """
        This function prints the current game board.
        """
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[:3]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[3:6]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[6:9]])+'\n')

    def posToLocalBoardIdx(self,row,col):
        return row * 3 + col
    
    def getLocalBoard(self, board_idx):
        local_board = {}
        local_origin = self.globalIdx[board_idx]
        for row in range(3):
            local_board[row] = list()
            for col in range(3):
                val = self.board[local_origin[0] + row][local_origin[1] + col]
                local_board[row].append(val)
                local_board[(row,col)] = val

        return local_board
    
    def getBoardAxisData(self):
        output = []
        for board_idx in range(9):
            output.append(list())
            local_board = self.getLocalBoard(board_idx)
            # print(local_board)
            for axis in self.board_axis:
                product = 1
                for pos in axis:
                    if local_board[pos] == self.maxPlayer:
                        product *= 3
                    elif local_board[pos] == self.minPlayer:
                        product *= 2
                output[board_idx].append(product)
        return output

    def getBoardSpaceData(self):
        output = []
        for spot_idx in range(9):
            count = 0
            for board_idx in range(9):
                if board_idx == spot_idx:
                    continue
                if self.board[(board_idx // 3) * 3 + (spot_idx // 3)][(board_idx % 3) * 3 + (spot_idx % 3)] == "_":
                    count += 1
            output.append(count)
        return output

    def getBoardAxis(self):
        output = []
        for board_idx in range(9):
            local_board = self.getLocalBoard(board_idx)
            # print(local_board)
            for axis in self.board_axis:
                product = 1
                for pos in axis:
                    if local_board[pos] == self.maxPlayer:
                        product *= 3
                    elif local_board[pos] == self.minPlayer:
                        product *= 2
                output.append(product)
        return Counter(output)

    def evaluatePredifined(self, isMax):
        if isMax:

            axis = self.getBoardAxis()

            # rule 1
            if self.axis_max_win in axis:
                # print("Rule 1")
                return self.winnerMaxUtility

            # rule 2
            elif self.axis_max_pot in axis or self.axis_max_block in axis:
                # print("Rule 2")
                score = 0
                if self.axis_max_pot in axis:
                    score += axis[self.axis_max_pot]*self.twoInARowMaxUtility
                if self.axis_max_block in axis:
                    score += axis[self.axis_max_block]*self.preventThreeInARowMaxUtility
                return score

            # rule 3
            else:
                # print("Rule 3")
                score = 0
                for corner in self.board_corners:
                    if self.board[corner[0]][corner[1]] == self.maxPlayer:
                        score += self.cornerMaxUtility
                return score

        else:

            axis = self.getBoardAxis()

            # rule 1
            if self.axis_min_win in axis:
                # print("Rule 1")
                return self.winnerMinUtility

            # rule 2
            elif self.axis_min_pot in axis or self.axis_min_block in axis:
                # print("Rule 2")
                score = 0
                if self.axis_min_pot in axis:
                    score += axis[self.axis_min_pot]*self.twoInARowMinUtility
                if self.axis_min_block in axis:
                    score += axis[self.axis_min_block]*self.preventThreeInARowMinUtility
                return score

            # rule 3
            else:
                # print("Rule 3")
                score = 0
                for corner in self.board_corners:
                    if self.board[corner[0]][corner[1]] == self.minPlayer:
                        score += self.cornerMinUtility
                return score

    def evaluateDesigned(self, isMax):
        """
        This function implements the evaluation function for ultimate tic tac toe for your own agent.
        input args:
        isMax(bool): boolean variable indicates whether it's maxPlayer or minPlayer.
                     True for maxPlayer, False for minPlayer
        output:
        score(float): estimated utility score for maxPlayer or minPlayer
        """
        if isMax:

            axis = self.getBoardAxis()
            axisData = self.getBoardAxisData()
            spaceData = self.getBoardSpaceData()

            # rule 1
            if self.axis_min_win in axis:
                return +10000
            elif self.axis_max_win in axis:
                return -10000

            score = 0
            for i, boardAxis in enumerate(axisData):
                if self.axis_min_pot in boardAxis:
                    score += 5 * spaceData[i]
                if self.axis_max_pot in boardAxis:
                    score -= 4 * spaceData[i]
                    
            return score

        else:

            axis = self.getBoardAxis()
            axisData = self.getBoardAxisData()
            spaceData = self.getBoardSpaceData()

            # rule 1
            if self.axis_min_win in axis:
                return -10000
            elif self.axis_max_win in axis:
                return +10000

            score = 0
            for i, boardAxis in enumerate(axisData):
                if self.axis_min_pot in boardAxis:
                    score -= 5 * spaceData[i]
                if self.axis_max_pot in boardAxis:
                    score += 4 * spaceData[i]
                    
            return score

    def checkMovesLeft(self):
        """
        This function checks whether any legal move remains on the board.
        output:
        movesLeft(bool): boolean variable indicates whether any legal move remains
                        on the board.
        """
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == "_":
                    return True
        return False

    def checkMovesLeftInLocalBoard(self):
        """
        This function checks whether any legal move remains on the board.
        output:
        movesLeft(bool): boolean variable indicates whether any legal move remains
                        on the board.
        """

        if self.checkWinner() != 0:
            return False

        local_board = self.getLocalBoard(self.startBoardIdx)
        for row in range(3):
            for col in range(3):
                if local_board[row][col] == "_":
                    return True
        return False

    def checkWinner(self):
        #Return termimnal node status for maximizer player 1-win,0-tie,-1-lose
        """
        This function checks whether there is a winner on the board.
        output:
        winner(int): Return 0 if there is no winner.
                     Return 1 if maxPlayer is the winner.
                     Return -1 if miniPlayer is the winner.
        """
        axis = self.getBoardAxis()
        if self.axis_max_win in axis:
            return 1
        elif self.axis_min_win in axis:
            return -1
        else:
            return 0

    def alphabeta(self, depth, currBoardIdx, alpha, beta, isMax):

        """
        This function implements alpha-beta algorithm for ultimate tic-tac-toe game.
        input args:
        depth(int): current depth level
        currBoardIdx(int): current local board index
        alpha(float): alpha value
        beta(float): beta value
        isMax(bool):boolean variable indicates whether it's maxPlayer or minPlayer.
                     True for maxPlayer, False for minPlayer
        output:
        bestValue(float):the bestValue that current player may have
        """

        return self.alphabetaBestMove(depth, currBoardIdx, alpha, beta, isMax, self.evaluatePredifined)[0]

    def alphabetaBestMove(self,depth,currBoardIdx,alpha,beta,isMax, evaluate):
        
        maxTurn = isMax != bool(depth % 2 == 1)

        if depth < self.maxDepth and self.checkMovesLeftInLocalBoard():

            local_board = self.getLocalBoard(currBoardIdx)

            scores = []

            for row in range(3):
                for col in range(3):
                    if local_board[row][col] == "_":

                        self.expandedNodes += 1

                        next_board_index = self.posToLocalBoardIdx(row,col)

                        offset = self.globalIdx[currBoardIdx]

                        if maxTurn:
                            self.board[offset[0] + row][offset[1] + col] = self.maxPlayer
                        else:
                            self.board[offset[0] + row][offset[1] + col] = self.minPlayer
                        
                        (new_score, (new_row, new_col)) = self.alphabetaBestMove(depth + 1, next_board_index, alpha, beta, isMax, evaluate)

                        self.board[offset[0] + row][offset[1] + col] = "_"

                        score_entry = (new_score, (row, col))

                        if maxTurn:
                            if new_score >= beta:
                                return score_entry
                            elif new_score > alpha:
                                alpha = new_score
                        else:
                            if new_score <= alpha:
                                return score_entry
                            elif new_score > beta:
                                beta = new_score

                        scores.append(score_entry)

            if len(scores) > 0:

                if maxTurn:
                    return max(scores, key = lambda x : x[0])
                else:
                    return min(scores, key = lambda x : x[0])
                
            else:
                return (evaluate(isMax), (0,0))
        else:
            return (evaluate(isMax), (0,0))
        return 0

    def minimax(self, depth, currBoardIdx, isMax):

        """
        This function implements minimax algorithm for ultimate tic-tac-toe game.
        input args:
        depth(int): current depth level
        currBoardIdx(int): current local board index
        alpha(float): alpha value
        beta(float): beta value
        isMax(bool):boolean variable indicates whether it's maxPlayer or minPlayer.
                     True for maxPlayer, False for minPlayer
        output:
        bestValue(float):the bestValue that current player may have
        """

        return self.minimaxBestMove(depth, currBoardIdx, isMax)[0]

    def minimaxBestMove(self, depth, currBoardIdx, isMax):

        maxTurn = isMax != bool(depth % 2 == 1)

        if depth < self.maxDepth and self.checkMovesLeftInLocalBoard():

            local_board = self.getLocalBoard(currBoardIdx)

            scores = []

            for row in range(3):
                for col in range(3):
                    if local_board[row][col] == "_":

                        self.expandedNodes += 1

                        next_board_index = self.posToLocalBoardIdx(row,col)

                        offset = self.globalIdx[currBoardIdx]

                        if maxTurn:
                            self.board[offset[0] + row][offset[1] + col] = self.maxPlayer
                        else:
                            self.board[offset[0] + row][offset[1] + col] = self.minPlayer
                        
                        (new_score, (new_row, new_col)) = self.minimaxBestMove(depth + 1, next_board_index, isMax)

                        # if new_score == 0 and depth == 2:
                        #     self.printGameBoard()
                        #     print("----------------------------------------------------------")

                        self.board[offset[0] + row][offset[1] + col] = "_"

                        score_entry = (new_score, (row, col))

                        scores.append(score_entry)

            if len(scores) > 0:

                if maxTurn:
                    return max(scores, key = lambda x : x[0])
                else:
                    return min(scores, key = lambda x : x[0])
            else:
                return (self.evaluatePredifined(isMax), (0,0))
        else:
            return (self.evaluatePredifined(isMax), (0,0))

    def playGamePredifinedAgent(self,maxFirst,isMinimaxOffensive,isMinimaxDefensive):
        """
        This function implements the processes of the game of predifined offensive agent vs defensive agent.
        input args:
        maxFirst(bool): boolean variable indicates whether maxPlayer or minPlayer plays first.
                        True for maxPlayer plays first, and False for minPlayer plays first.
        isMinimaxOffensive(bool):boolean variable indicates whether it's using minimax or alpha-beta pruning algorithm for offensive agent.
                        True is minimax and False is alpha-beta.
        isMinimaxOffensive(bool):boolean variable indicates whether it's using minimax or alpha-beta pruning algorithm for defensive agent.
                        True is minimax and False is alpha-beta.
        output:
        bestMove(list of tuple): list of bestMove coordinates at each step
        bestValue(list of float): list of bestValue at each move
        expandedNodes(list of int): list of expanded nodes at each move
        gameBoards(list of 2d lists): list of game board positions at each move
        winner(int): 1 for maxPlayer is the winner, -1 for minPlayer is the winner, and 0 for tie.
        """

        bestMove=[]
        bestValue=[]
        gameBoards=[]
        expandedNodesList = []
        
        maxTurn = maxFirst

        self.currBoardIdx = self.startBoardIdx

        while self.checkMovesLeftInLocalBoard():

            offset = self.globalIdx[self.currBoardIdx]

            if maxTurn:
                if isMinimaxOffensive:
                    (val, move) = self.minimaxBestMove(0, self.currBoardIdx, maxTurn)
                else:
                    (val, move) = self.alphabetaBestMove(0, self.currBoardIdx, float("-inf"),float("inf"), maxTurn, self.evaluatePredifined)
            else:
                if isMinimaxDefensive:
                    (val, move) = self.minimaxBestMove(0, self.currBoardIdx, maxTurn)
                else:
                    (val, move) = self.alphabetaBestMove(0, self.currBoardIdx, float("-inf"),float("inf"), maxTurn, self.evaluatePredifined)

            expandedNodesList.append(self.expandedNodes)
            self.expandedNodes = 0

            self.currBoardIdx = self.posToLocalBoardIdx(move[0],move[1])

            move = (offset[0] + move[0], offset[1] + move[1])

            bestMove.append(move)

            bestValue.append(val)

            self.board[move[0]][move[1]] = self.maxPlayer if maxTurn else self.minPlayer

            gameBoards.append(deepcopy(self.board))

            maxTurn = not maxTurn

        return gameBoards, bestMove, expandedNodesList, bestValue, self.checkWinner()

    def playGameYourAgent(self, maxFirst=-1,startSpace=9):
        """
        This function implements the processes of the game of your own agent vs predifined offensive agent.
        input args:
        output:
        bestMove(list of tuple): list of bestMove coordinates at each step
        gameBoards(list of 2d lists): list of game board positions at each move
        winner(int): 1 for maxPlayer is the winner, -1 for minPlayer is the winner, and 0 for tie.
        """
        bestMove=[]
        bestValue=[]
        gameBoards=[]
        
        maxTurn = bool(randint(0,1) == 1)
        if maxFirst != -1:
            maxTurn = bool(maxFirst)

        self.startBoardIdx = randint(0,8)

        if startSpace != 9:
            self.startBoardIdx = startSpace

        self.currBoardIdx = self.startBoardIdx

        while self.checkMovesLeftInLocalBoard():

            offset = self.globalIdx[self.currBoardIdx]

            (val, move) = self.alphabetaBestMove(0, self.currBoardIdx, float("-inf"),float("inf"), maxTurn, self.evaluatePredifined if maxTurn else self.evaluateDesigned)

            self.currBoardIdx = self.posToLocalBoardIdx(move[0],move[1])

            move = (offset[0] + move[0], offset[1] + move[1])

            bestMove.append(move)

            bestValue.append(val)

            self.board[move[0]][move[1]] = self.maxPlayer if maxTurn else self.minPlayer

            gameBoards.append(deepcopy(self.board))

            maxTurn = not maxTurn

        return gameBoards, bestMove, self.checkWinner()



    def getHumanMove(self):

        offset = self.globalIdx[self.currBoardIdx]
        print("")
        move_options = set()
        for row in range(9):
            print("++---+---+---++---+---+---++---+---+---++")
            if row % 3 == 0  and row != 0:
                print("++---+---+---++---+---+---++---+---+---++")
            row_str = "|"
            for col in range(9):
                if col % 3 == 0:
                    row_str += "|"
                if row >= offset[0] and row < offset[0] + 3 and col >= offset[1] and col < offset[1] + 3:
                    if self.board[row][col] == "_":
                        row_str += " " + str((row % 3) * 3 + col % 3) + " |"
                        move_options.add((row % 3) * 3 + col % 3)
                    else:
                        row_str += " " + self.board[row][col] + " |"
                else:
                    row_str += " " + self.board[row][col] + " |"
            row_str += "|"
            print(row_str)
        print("++---+---+---++---+---+---++---+---+---++")
        playerMove = 9
        while playerMove not in move_options:
            playerMove = int(input("Enter Your Move: "))
            print(move_options)
            print("+---------------------------------------+")
        
        return (playerMove // 3, playerMove % 3)

    def playGameHuman(self):

        """
        This function implements the processes of the game of your own agent vs a human.
        output:
        bestMove(list of tuple): list of bestMove coordinates at each step
        gameBoards(list of 2d lists): list of game board positions at each move
        winner(int): 1 for maxPlayer is the winner, -1 for minPlayer is the winner, and 0 for tie.
        """

        bestMove=[]
        gameBoards=[]

        maxTurn = bool(randint(0,1) == 1)
        self.startBoardIdx = randint(0,8)
        
        self.currBoardIdx = self.startBoardIdx

        while self.checkMovesLeftInLocalBoard():

            if maxTurn:

                offset = self.globalIdx[self.currBoardIdx]

                move = self.getHumanMove()

                self.currBoardIdx = self.posToLocalBoardIdx(move[0],move[1])

                move = (offset[0] + move[0], offset[1] + move[1])

            else:
                offset = self.globalIdx[self.currBoardIdx]

                (val, move) = self.alphabetaBestMove(0, self.currBoardIdx, float("-inf"),float("inf"), maxTurn, self.evaluateDesigned)

                self.currBoardIdx = self.posToLocalBoardIdx(move[0],move[1])

                move = (offset[0] + move[0], offset[1] + move[1])

                bestMove.append(move)

            self.board[move[0]][move[1]] = self.maxPlayer if maxTurn else self.minPlayer
            
            gameBoards.append(deepcopy(self.board))

            maxTurn = not maxTurn

        return gameBoards, bestMove, self.checkWinner()

if __name__=="__main__":
    uttt=ultimateTicTacToe()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(True,False,False)
    print("--------------------------------")
    print("\tAlphaBeta vs. AlphaBeta")
    print("\tMax First")
    print("--------------------------------")
    print("Expanded Nodes: " + str(expandedNodes))
    print("Expanded Nodes: " + str(bestValue))
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    uttt.printGameBoard()

    uttt=ultimateTicTacToe()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(True,False,True)
    print("--------------------------------")
    print("\tAlphaBeta vs. Minimax")
    print("\tMax First")
    print("--------------------------------")
    print("Expanded Nodes: " + str(expandedNodes))
    print("Expanded Nodes: " + str(bestValue))
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    uttt.printGameBoard()

    uttt=ultimateTicTacToe()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(True,True,False)
    print("--------------------------------")
    print("\tMinimax vs. AlphaBeta")
    print("\tMax First")
    print("--------------------------------")
    print("Expanded Nodes: " + str(expandedNodes))
    print("Expanded Nodes: " + str(bestValue))
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    uttt.printGameBoard()

    uttt=ultimateTicTacToe()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(True,True,True)
    print("--------------------------------")
    print("\tMinimax vs. Minimax")
    print("\tMax First")
    print("--------------------------------")
    print("Expanded Nodes: " + str(expandedNodes))
    print("Expanded Nodes: " + str(bestValue))
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    uttt.printGameBoard()

    uttt=ultimateTicTacToe()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False,False,False)
    print("--------------------------------")
    print("\tAlphaBeta vs. AlphaBeta")
    print("\tMin First")
    print("--------------------------------")
    print("Expanded Nodes: " + str(expandedNodes))
    print("Expanded Nodes: " + str(bestValue))
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    uttt.printGameBoard()

    uttt=ultimateTicTacToe()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False,False,True)
    print("--------------------------------")
    print("\tAlphaBeta vs. Minimax")
    print("\tMin First")
    print("--------------------------------")
    print("Expanded Nodes: " + str(expandedNodes))
    print("Expanded Nodes: " + str(bestValue))
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    uttt.printGameBoard()

    uttt=ultimateTicTacToe()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False,True,False)
    print("--------------------------------")
    print("\tMinimax vs. AlphaBeta")
    print("\tMin First")
    print("--------------------------------")
    print("Expanded Nodes: " + str(expandedNodes))
    print("Expanded Nodes: " + str(bestValue))
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    uttt.printGameBoard()

    uttt=ultimateTicTacToe()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False,True,True)
    print("--------------------------------")
    print("\tMinimax vs. Minimax")
    print("\tMin First")
    print("--------------------------------")
    print("Expanded Nodes: " + str(expandedNodes))
    print("Expanded Nodes: " + str(bestValue))
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    uttt.printGameBoard()

    sum = 0
    for i in range(2):
        for j in range(9):
            uttt=ultimateTicTacToe()
            gameBoards, bestMove, winner = uttt.playGameYourAgent(True if i == 1 else False, j)
            sum += winner
    print(f"Defined Agent Win Percentage: {(18.0 - sum)/2.0/18.0*100}%")

    uttt=ultimateTicTacToe()
    gameBoards, bestMove, winner = uttt.playGameHuman()
    if winner == 1:
        print("You Win!!!")
    elif winner == -1:
        print("You Lost!!!")
    else:
        print("Tie. No winner:(")
