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
    
    def getLocalBoard(self, board, board_idx):
        local_board = {}
        local_origin = self.globalIdx[board_idx]
        for row in range(3):
            local_board[row] = list()
            for col in range(3):
                val = board[local_origin[0] + row][local_origin[1] + col]
                local_board[row].append(val)
                local_board[(row,col)] = val

        return local_board
    
    def getBoardAxis(self,board):
        output = []
        for board_idx in range(9):
            local_board = self.getLocalBoard(board, board_idx)
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
        
    def utilityFunction(self, board, isMax):    
        
        if isMax:

            axis = self.getBoardAxis(board)

            # rule 1
            if self.axis_max_win in axis:
                return self.winnerMaxUtility

            # rule 2
            elif self.axis_max_pot in axis or self.axis_max_block in axis:
                score = 0
                if self.axis_max_pot in axis:
                    score += axis[self.axis_max_pot]*self.twoInARowMaxUtility
                if self.axis_max_block in axis:
                    score += axis[self.axis_max_block]*self.preventThreeInARowMaxUtility
                return score

            # rule 3
            else:
                score = 0
                for corner in self.board_corners:
                    if board[corner[0]][corner[1]] == self.maxPlayer:
                        score += self.cornerMaxUtility
                return score

        else:

            axis = self.getBoardAxis(board)

            # rule 1
            if self.axis_min_win in axis:
                return self.winnerMinUtility

            # rule 2
            elif self.axis_min_pot in axis or self.axis_min_block in axis:
                score = 0
                if self.axis_min_pot in axis:
                    score += axis[self.axis_min_pot]*self.twoInARowMinUtility
                if self.axis_min_block in axis:
                    score += axis[self.axis_min_block]*self.preventThreeInARowMinUtility
                return score

            # rule 3
            else:
                score = 0
                for corner in self.board_corners:
                    if board[corner[0]][corner[1]] == self.maxPlayer:
                        score += self.cornerMinUtility
                return score
        
    def localBoardHasMovesLeft(self, board, lb):
        
        for i in range(lb[0], lb[0] + 3):
            for j in range(lb[1], lb[1] + 3):
                if board[i][j] == '_':
                    return True
        return False
        
    def getNextBoard(self, move, lb):
        return self.globalIdx.index(((move[0] - lb[0])*3,(move[1] - lb[1])*3))
        
        
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
        axis_scores = self.getBoardAxis(self.board)
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
        return self.alphaBetaBoard(self.board, depth, currBoardIdx, alpha, beta, isMax, [])[0]

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
        return self.minimaxBoard(self.board, depth, currBoardIdx, isMax, [])[0]
    
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
                        nextBoardIdx = self.getNextBoard((i,j), lb)
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
                        nextBoardIdx = self.getNextBoard((i,j), lb)
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
                else:
                    v = self.alphaBetaBoard(self.board, 0, nextBoardIdx, -sys.maxsize, sys.maxsize, True, [])
                    
                best_move, best_val = v[1][0], v[0]
                self.board[best_move[0]][best_move[1]] = self.maxPlayer
                
                #print("1:", best_move, lb, nextBoardIdx, best_val)
                nextBoardIdx = self.getNextBoard(best_move, lb)
                bestMove, bestValue, gameBoards = bestMove+[best_move], bestValue+[best_val], gameBoards+[deepcopy(self.board)]
            
            maxFirst = True
            
            lb = self.globalIdx[nextBoardIdx]
            if isMinimaxDefensive:
                v = self.minimaxBoard(self.board, 0, nextBoardIdx, False, [])
            else:
                v = self.alphaBetaBoard(self.board, 0, nextBoardIdx, -sys.maxsize, sys.maxsize, False, [])
                
            best_move, best_val = v[1][0], v[0]
            self.board[best_move[0]][best_move[1]] = self.minPlayer
            
            #print("2:", best_move, lb, nextBoardIdx, best_val)            
            nextBoardIdx = self.getNextBoard(best_move, lb)
            bestMove, bestValue, gameBoards = bestMove+[best_move], bestValue+[best_val], gameBoards+[deepcopy(self.board)]
                     
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
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False,True,True)
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    print(uttt.startBoardIdx)
    end = time.process_time()
    print('Minimax-Minimax', end-start)
    
    uttt=ultimateTicTacToe()
    start = time.process_time()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False,False,True)
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    print(uttt.startBoardIdx)
    end = time.process_time()
    print('Alphabeta-Minimax', end-start)
    
    uttt=ultimateTicTacToe()
    start = time.process_time()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False, True, False)
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    print(uttt.startBoardIdx)
    end = time.process_time()
    print('Minimax-Alphabeta', end-start)
    
    uttt=ultimateTicTacToe()
    start = time.process_time()
    gameBoards, bestMove, expandedNodes, bestValue, winner=uttt.playGamePredifinedAgent(False, False, False)
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
    print(uttt.startBoardIdx)
    end = time.process_time()
    print('Alphabeta-Alphabeta', end-start)
    
    
    #for b in gameBoards:
        #uttt.printBoard(b)
    
    #print(bestMove, bestValue)
    #print('Winner', winner)
    
    # if winner == 1:
    #     print("The winner is maxPlayer!!!")
    # elif winner == -1:
    #     print("The winner is minPlayer!!!")
    # else:
    #     print("Tie. No winner:(")
