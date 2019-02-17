from time import sleep
from math import inf
from random import randint
from copy import deepcopy
from collections import Counter
import sys
import time

class ultimateTicTacToe:
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

        #utility value for reflex offensive and reflex defensive agents
        self.winnerMaxUtility=10000
        self.twoInARowMaxUtility=500
        self.preventThreeInARowMaxUtility=100
        self.cornerMaxUtility=30

        self.winnerMinUtility=-10000
        self.twoInARowMinUtility=-100
        self.preventThreeInARowMinUtility=-500
        self.cornerMinUtility=-30
        self.ctr = 1
        self.expandedNodes=0
        self.currPlayer=True

    def printGameBoard(self):
        """
        This function prints the current game board.
        """
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[:3]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[3:6]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[6:9]])+'\n')

    def printBoard(self, board):
        """
        This function prints the current game board.
        """
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in board[:3]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in board[3:6]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in board[6:9]])+'\n')
        print(self.ctr)
    
    def getAxisScores(self, board):
    
        # A product of 27 implies all X's in a row
        # A product of 8 implies all O's in a row
        # A product of 18 implies 2 X's and 1 O's in a row
        # A product of 12 implies 1 X's and 2 O's in a row
        # A product of 1 implies all blanks
        # A product of 9 implies 2 X's
        # A product of 4 implies 2 O's in a row
        
        b = deepcopy(self.board)
        score = 0
        for i in range(len(b)):
            for j in range(len(b[0])):
                if b[i][j] == self.minPlayer:
                    b[i][j] = 2
                elif b[i][j] == self.maxPlayer:
                    b[i][j] = 3
                else:
                    b[i][j] = 1
        
        axis_scores = []
        #YOUR CODE HERE
        for lb in self.globalIdx:
            for i in range(lb[0], lb[0] + 3):
                s = b[i][lb[1]] * b[i][lb[1] + 1] * b[i][lb[1] + 2]
                axis_scores.append(s)
            for j in range(lb[1], lb[1] + 3):
                s = b[lb[0]][j] * b[lb[0] + 1][j] * b[lb[0] + 2][j]
                axis_scores.append(s)
            
            d1 = b[lb[0]][lb[1]] * b[lb[0] + 1][lb[1] + 1] * b[lb[0] + 2][lb[1] + 2]
            axis_scores.append(d1)
            d2 = b[lb[0]][lb[1] + 2] * b[lb[0] + 1][lb[1] + 1] * b[lb[0] + 2][lb[1] + 0]
            axis_scores.append(d2)
        
        
        return Counter(axis_scores)
        
        
    def utilityFunction(self, board, isMax):    
        axis_scores = self.getAxisScores(board)
        score = 0
        if isMax:
            if 27 in axis_scores:
                #Victory Condition
                score+=10000
            else:
                if 9 in axis_scores:
                    score+=(axis_scores[9]*500)
                if 12 in axis_scores:
                    score+=(axis_scores[12]*100)
        else:
            if 8 in axis_scores:
                #Victory Condition
                score-=10000
            else:
                if 4 in axis_scores:
                    score-=(axis_scores[4]*100)
                if 18 in axis_scores:
                    score-=(axis_scores[18]*500)
        
        #Third rule
        corner_element = self.maxPlayer if isMax else self.minPlayer
        corner_score = 0
        b = board
        if score == 0:
            for lb in self.globalIdx:
                if b[lb[0]][lb[1]] == corner_element:
                    corner_score+=30
                if b[lb[0] + 2][lb[1]] == corner_element:
                    corner_score+=30
                if b[lb[0]][lb[1] + 2] == corner_element:
                    corner_score+=30
                if b[lb[0] + 2][lb[1] + 2] == corner_element:
                    corner_score+=30
        if isMax:
            score+=corner_score
        else:
            score-=corner_score
        return score
        
    def localBoardHasMovesLeft(self, board, lb):
        
        for i in range(lb[0], lb[0] + 3):
            for j in range(lb[1], lb[1] + 3):
                if board[i][j] == '_':
                    return True
        return False
        
    def evaluatePredifined(self, isMax):
        """
        This function implements the evaluation function for ultimate tic tac toe for predifined agent.
        input args:
        isMax(bool): boolean variable indicates whether it's maxPlayer or minPlayer.
                     True for maxPlayer, False for minPlayer
        output:
        score(float): estimated utility score for maxPlayer or minPlayer
        """
        return utilityFunction(self.board, isMax)

    def evaluateDesigned(self, isMax):
        """
        This function implements the evaluation function for ultimate tic tac toe for your own agent.
        input args:
        isMax(bool): boolean variable indicates whether it's maxPlayer or minPlayer.
                     True for maxPlayer, False for minPlayer
        output:
        score(float): estimated utility score for maxPlayer or minPlayer
        """
        #YOUR CODE HERE
            
        
        score=0
        return score

    def checkMovesLeft(self):
        """
        This function checks whether any legal move remains on the board.
        output:
        movesLeft(bool): boolean variable indicates whether any legal move remains
                        on the board.
        """
        #YOUR CODE HERE
        if self.checkWinner() != 0:
            return False
        for lb in self.globalIdx:
            if self.localBoardHasMovesLeft(self.board, lb):
                return True
                

    def checkWinner(self):
        #Return termimnal node status for maximizer player 1-win,0-tie,-1-lose
        """
        This function checks whether there is a winner on the board.
        output:
        winner(int): Return 0 if there is no winner.
                     Return 1 if maxPlayer is the winner.
                     Return -1 if miniPlayer is the winner.
        """
        axis_scores = self.getAxisScores(self.board)
        if 27 in axis_scores:
            return 1
        elif 8 in axis_scores:
            return -1
        return 0

    def alphabeta(self,depth,currBoardIdx,alpha,beta,isMax):
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
        #YOUR CODE HERE
        return self.alphaBetaBoard(self.board, depth, currBoardIdx, alpha, beta, isMax)

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
        #YOUR CODE HERE
        return self.minimaxBoard(self.board, depth, currBoardIdx, isMax)                    
    
    def minimaxBoard(self, board, depth, currBoardIdx, isMax, moves):
        #YOUR CODE HERE
        bestValue=0.0
        scores = []
        lb = self.globalIdx[currBoardIdx]
        
        if depth < self.maxDepth:
            for i in range(lb[0], lb[0] + 3):
                for j in range(lb[1], lb[1] + 3):
                    # Check its a valid slot
                    if board[i][j] == '_':
                        b = deepcopy(board)
                        b[i][j] = self.maxPlayer if isMax else self.minPlayer
                        nextBoardIdx = self.globalIdx.index(((i - lb[0])*3,(j - lb[1])*3))
                        s = self.minimaxBoard(b, depth + 1, nextBoardIdx,not isMax, moves + [(i,j)])
                        scores.append(s)
            if isMax:
                return max(scores, key=lambda x:x[0])
            else:
                return min(scores, key=lambda x:x[0])
        else:            
            return self.utilityFunction(board, isMax), moves
        
    
    def alphaBetaBoard(self, board, depth, currBoardIdx, alpha, beta, isMax, moves):
        #YOUR CODE HERE
        bestValue=0.0
        scores = []
        lb = self.globalIdx[currBoardIdx]
        
        if depth < self.maxDepth:
            for i in range(lb[0], lb[0] + 3):
                for j in range(lb[1], lb[1] + 3):
                    # Check its a valid slot
                    if board[i][j] == '_':
                        b = deepcopy(board)
                        b[i][j] = self.maxPlayer if isMax else self.minPlayer
                        nextBoardIdx = self.globalIdx.index(((i - lb[0])*3,(j - lb[1])*3))
                        s = self.alphaBetaBoard(b, depth + 1, nextBoardIdx, alpha, beta, not isMax, moves + [(i,j)])
                        scores.append(s)
                        if isMax:
                            v = max(scores, key=lambda x:x[0])
                            if v[0] >= beta:
                                return v
                            alpha = max(alpha, v[0])
                        else:
                            v = min(scores, key=lambda x:x[0])
                            if v[0] <= alpha: 
                                return v
                            beta = min(beta, v[0])
            return v
        else:            
            #self.printBoard(board)
            #self.ctr+=1
            return self.utilityFunction(board, isMax), moves
    
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
        #YOUR CODE HERE
        # For now max always plays first
        bestMove=[]
        bestValue=[]
        gameBoards=[]
        
        nextBoardIdx = self.startBoardIdx
        while self.checkMovesLeft():
        
            if maxFirst:
                lb = self.globalIdx[nextBoardIdx]
                if isMinimaxOffensive:
                    v = self.minimaxBoard(self.board, 0, nextBoardIdx, True, [])
                    best_move, best_val = v[1][0], v[0]
                    # max_scores = []
                    # for i in range(lb[0], lb[0] + 3):
                        # for j in range(lb[1], lb[1] + 3):
                            # # Check its a valid slot
                            # if self.board[i][j] == '_':
                                # b = deepcopy(self.board)
                                # b[i][j] = self.maxPlayer
                                # temp_nextBoardIdx = self.globalIdx.index(((i - lb[0])*3,(j - lb[1])*3))
                                # maxValue = self.minimaxBoard(b, 1, temp_nextBoardIdx, False)
                                # max_scores.append(((i,j), maxValue))
                            
                    # best_move, best_val = max(max_scores, key=lambda x:x[1])
                    
                else:
                    v = self.alphaBetaBoard(self.board, 0, nextBoardIdx, -sys.maxsize, sys.maxsize, True, [])
                    # for i in range(lb[0], lb[0] + 3):
                        # for j in range(lb[1], lb[1] + 3):
                            # #Check its a valid slot
                            # if self.board[i][j] == '_':
                                # b = deepcopy(self.board)
                                # b[i][j] = self.maxPlayer
                                # temp_nextBoardIdx = self.globalIdx.index(((i - lb[0])*3,(j - lb[1])*3))
                                # action_val = self.alphaBetaBoard(self.board, 1, temp_nextBoardIdx, -sys.maxsize, sys.maxsize, False)
                                # if v == action_val:
                                    # best_move = (i,j)
                                    # best_val = action_val
                                    # break
                        # if v == action_val:
                            # break
                    best_move, best_val = v[1][0], v[0]
                    
                self.board[best_move[0]][best_move[1]] = self.maxPlayer
                print("1:", best_move, lb, nextBoardIdx, best_val)
                nextBoardIdx = self.globalIdx.index(((best_move[0] - lb[0])*3,(best_move[1] - lb[1])*3))
                bestMove.append(best_move)
                bestValue.append(best_val)
                gameBoards.append(deepcopy(self.board))
            
            maxFirst = True
            
            lb = self.globalIdx[nextBoardIdx]
            v = self.minimaxBoard(self.board, 0, nextBoardIdx, False, [])
            best_move, best_val = v[1][0], v[0]
            # min_scores = []
            # for i in range(lb[0], lb[0] + 3):
                # for j in range(lb[1], lb[1] + 3):
                    # # Check its a valid slot
                    # if self.board[i][j] == '_':
                        # b = deepcopy(self.board)
                        # b[i][j] = self.minPlayer
                        # temp_nextBoardIdx = self.globalIdx.index(((i - lb[0])*3,(j - lb[1])*3))
                        # minValue = self.minimaxBoard(b, 1, temp_nextBoardIdx, True)
                        # min_scores.append(((i,j), minValue))
                        
            #best_move, best_val = min(min_scores, key=lambda x:x[1])
            print("2:", best_move, lb, nextBoardIdx, best_val)
            self.board[best_move[0]][best_move[1]] = self.minPlayer
            nextBoardIdx = self.globalIdx.index(((best_move[0] - lb[0])*3,(best_move[1] - lb[1])*3))
            
            bestMove.append(best_move)
            bestValue.append(best_val)
            gameBoards.append(deepcopy(self.board))
                     
        winner = self.checkWinner()
        expandedNodes = []
        return gameBoards, bestMove, expandedNodes, bestValue, winner

    def playGameYourAgent(self):
        """
        This function implements the processes of the game of your own agent vs predifined offensive agent.
        input args:
        output:
        bestMove(list of tuple): list of bestMove coordinates at each step
        gameBoards(list of 2d lists): list of game board positions at each move
        winner(int): 1 for maxPlayer is the winner, -1 for minPlayer is the winner, and 0 for tie.
        """
        #YOUR CODE HERE
        bestMove=[]
        gameBoards=[]
        winner=0
        return gameBoards, bestMove, winner


    def playGameHuman(self):
        """
        This function implements the processes of the game of your own agent vs a human.
        output:
        bestMove(list of tuple): list of bestMove coordinates at each step
        gameBoards(list of 2d lists): list of game board positions at each move
        winner(int): 1 for maxPlayer is the winner, -1 for minPlayer is the winner, and 0 for tie.
        """
        #YOUR CODE HERE
        bestMove=[]
        gameBoards=[]
        winner=0
        return gameBoards, bestMove, winner

if __name__=="__main__":
    uttt=ultimateTicTacToe()
    start = time.process_time()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False,True,False)
    print(uttt.startBoardIdx)
    end = time.process_time()
    print('Minimax', end-start)
    uttt2=ultimateTicTacToe()
    start = time.process_time()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt2.playGamePredifinedAgent(False,False,False)
    print(uttt2.startBoardIdx)
    end = time.process_time()
    print('Alphabeta', end-start)
    #for b in gameBoards:
        #uttt.printBoard(b)
    
    #print(bestMove, bestValue)
    #print('Winner', winner)
    
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
