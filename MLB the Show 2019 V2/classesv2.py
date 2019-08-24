import random
import pandas as pd
import datetime as dt


class GlobalSwitch:
    DEBUG = False


class Utilities:
    def Pause():
        if GlobalSwitch.DEBUG == True:
            input('Press any key to continue...')


class Base:
    def __init__(self, name):
        self.Name = name
        self.PlayerHere = None


class Stat:
    def __init__(self, name, range):
        self.Name = name
        self.Value = range


class Pitcher:
    def __init__(self, name, myTeam,
                 bid, avgouts, SingleR,
                 DoubleR, TripleR, HomeRunR,
                 WalkR, SOR, FlyGrR, DPR, source):
        # general stats
        self.Name = name
        self.MyTeam = myTeam
        self.BID = bid
        self.Avgouts = avgouts

        # base stats

        self.SingleR = SingleR
        self.DoubleR = DoubleR
        self.TripleR = TripleR
        self.HomeRunR = HomeRunR
        self.WalkR = WalkR
        self.SOR = SOR
        self.FlyGrR = FlyGrR
        self.DPR = DPR
        self.Source = source


class Team:
    def __init__(self, name):
        self.Name = name
        self.Score = 0
        self.Players = None
        self.AccumulatedOuts = 0
        self.OutCount = 0
        self.CurrentPlayer = None
        self.CurrentIndex = 0
        self.Pitcher = None
        self.OpposingTeam = None
        self.Pitchers = None

    def GetPlayer(self):
        if (self.CurrentIndex > len(self.Players) - 1):
            self.CurrentIndex = 0

        return self.Players[self.CurrentIndex]

    def HalfInning(self, bases):
        teamIsIn = True

        while (teamIsIn):

            OpposingPitcherTeam = self.OpposingTeam
            #
            Activeplayer = self.GetPlayer()

            Activeplayer.swing(bases, OpposingPitcherTeam)

            # Activeplayer.PrintBasesStatus(bases)

            self.CurrentIndex += 1
            #			self.PrintScore()
            Utilities.Pause()
            if (self.OutCount >= 3):
                ResetBases(bases)
                teamIsIn = False
                return


# def PrintScore(self):
# print('DEBUG: Stats for ' + self.Name +
# ' Score: ' + str(self.Score) +
# ' Outs: ' + str(self.OutCount) +
# ' Total Outs: ' + str(self.AccumulatedOuts))

class Player:
    def __init__(self, name, myTeam,
                 bid, SingleR,
                 DoubleR, TripleR, HomeRunR,
                 WalkR, SOR, FlyGrR, DPR, source):
        # general stats
        self.Name = name
        self.MyTeam = myTeam
        self.BID = bid

        # base stats

        self.SingleR = SingleR
        self.DoubleR = DoubleR
        self.TripleR = TripleR
        self.HomeRunR = HomeRunR
        self.WalkR = WalkR
        self.SOR = SOR
        self.FlyGrR = FlyGrR
        self.DPR = DPR
        self.Source = source

    def swing(self, allBases, Opposingteam):

        if self.MyTeam.AccumulatedOuts < Opposingteam.Pitcher.Avgouts:

            #print(Opposingteam.Pitcher.Name)

            swingResult = self.getSwingResult(Opposingteam.Pitcher);

            #print(self.MyTeam.AccumulatedOuts)

            #print(self.Name + ' gets swingResult = ' + str(swingResult))

            if (swingResult > 0 and swingResult < 4):
                self.AdjustBases(swingResult, allBases)
                allBases[swingResult].PlayerHere = self
            elif (swingResult == 4):
                self.AdjustBases(swingResult, allBases)
                self.MyTeam.Score += 1
            elif (swingResult == 0):
                self.MyTeam.OutCount += 1
                self.MyTeam.AccumulatedOuts += 1

        else:
            Opposingteam.Pitcher = Opposingteam.Pitchers[1]

            #print(Opposingteam.Pitcher.Name)

            #print('\n' + Opposingteam.Pitcher.Name + ' is now pitching' + '\n')

            swingResult = self.getSwingResult(Opposingteam.Pitcher);

            #print(self.MyTeam.AccumulatedOuts)

            #print(self.Name + ' gets swingResult = ' + str(swingResult))

            if (swingResult > 0 and swingResult < 4):
                self.AdjustBases(swingResult, allBases)
                allBases[swingResult].PlayerHere = self
            elif (swingResult == 4):
                self.AdjustBases(swingResult, allBases)
                self.MyTeam.Score += 1
            elif (swingResult == 0):
                self.MyTeam.OutCount += 1
                self.MyTeam.AccumulatedOuts += 1

    def getSwingResult(self, OpposingPitcher):

        #print(OpposingPitcher.Name + ' pitched to ' + self.Name + '\n')

        result = -1

        p = OpposingPitcher

        # print(tempOBP)

        ball = random.randint(1, 1000)

        if p.TripleR == None:

            p.TripleR = 0

        else:

            p.TripleR = p.TripleR

        if self.TripleR == None:

            self.TripleR = 0

        else:

            self.TripleR = self.TripleR

        singleC = int(round((p.SingleR + self.SingleR) / 2))
        doubleC = int(round((p.DoubleR + self.DoubleR) / 2))
        tripleC = int(round((p.TripleR + self.TripleR) / 2))
        homerunC = int(round((p.HomeRunR + self.HomeRunR) / 2))
        walkC = int(round((p.WalkR + self.WalkR) / 2))
        soC = int(round((p.SOR + self.SOR) / 2))
        FlyGrC = int(round((p.FlyGrR + self.FlyGrR) / 2))
        DPC = int(round((p.DPR + self.DPR) / 2))

        total_range = 1001

        if tripleC == None:

            tripleC = 0

        else:

            tripleC = tripleC

        single = int(round(total_range - singleC))
        double = int(round(single - doubleC))
        triple = int(round(double - tripleC))
        homerun = int(round(triple - homerunC))
        walk = int(round(homerun - walkC))
        strikeout = int(round(walk - soC))
        field_out = int(round(strikeout - FlyGrC))
        double_play = int(round(field_out - DPC))

        if double == None:

            double = 0

        else:

            double = double

        # Converts range values to ranges per at bat result

        DPR = range(0, field_out)

        FlyGrR = range(field_out, strikeout)

        SOR = range(strikeout, walk)

        walkR = range(walk, homerun)

        homerunR = range(homerun, triple)

        tripleR = range(triple, double)

        doubleR = range(double, single)

        singleR = range(single, total_range)

        # assigns result of ab depending on where ball is in range

        if ball in DPR:

            result = 0

        elif ball in FlyGrR:

            result = 0


        elif ball in SOR:

            result = 0

        elif ball in walkR:

            result = 1

        elif ball in homerunR:

            result = 4

        elif ball in tripleR:

            result = 3

        elif ball in doubleR:

            result = 2

        elif ball in singleR:

            result = 1

        else:

            print('error')
            print(ball)
            print(self.Name)



        #def PrintBasesStatus(self, allBases):
            #for base in allBases:
                #if (base.PlayerHere != None):
                    #print('Name: ' + base.Name + '\t Player: ' + base.PlayerHere.Name)
                #else:
                    #print('Name: ' + base.Name + '\t Player: None')

        return result


    def AdjustBases(self, swingResult, allBases):
        count = 4
        for base in reversed(allBases):
            if (base.PlayerHere != None and count == 4 and swingResult >= 1):
                count -= 1
                # player is on Base 4 and swingResult is at least 1
                # remove player from bases list and add 1 to teams score
                base.PlayerHere = None
                self.MyTeam.Score += 1
            elif (base.PlayerHere != None and count == 3 and swingResult >= 2):
                count -= 1
                # player is on Base 3 and swingResult is at least 2
                # remove player from bases list and add 1 to teams score
                base.PlayerHere = None
                self.MyTeam.Score += 1
            elif (base.PlayerHere != None and count == 2 and swingResult >= 3):
                count -= 1
                # player is on Base 2 and swingResult is at least 3
                # remove player from bases list and add 1 to teams score
                base.PlayerHere = None
                self.MyTeam.Score += 1
            elif (base.PlayerHere != None and count == 1 and swingResult >= 4):
                count -= 1
                # player is on Base 1 and swingResult is at least 4
                # remove player from bases list and add 1 to teams score
                base.PlayerHere = None
                self.MyTeam.Score += 1
            elif (base.PlayerHere != None):
                count -= 1
                tempPlayer = base.PlayerHere

                allBases[count + swingResult].PlayerHere = tempPlayer
                base.PlayerHere = None
            else:
                count -= 1


class Game:
    def __init__(self, team1, team2):
        self.Team1 = team1
        self.Team2 = team2
        self.CurrentInning = 0
        self.Team1wins = 0
        self.Team2wins = 0

    def PlayBall(self, bases):
        for i in range(1, 10):
            self.CurrentInning = i
            self.Team1.HalfInning(bases)
            self.Team1.OutCount = 0
            self.Team2.HalfInning(bases)
            self.Team2.OutCount = 0
            #self.PrintCurrentResults()
            # self.Team1.OpposingTeam = (Team2)
            # self.Team2.OpposingTeam = (Team1)
            Utilities.Pause()

    def PlayRepeat(self, iterations, bases):

        for i in range(0, iterations):

            self.PlayBall(bases)

            if self.Team1.Score > self.Team2.Score:
                self.Team1wins += 1
            elif self.Team2.Score > self.Team1.Score:
                self.Team2wins += 1
            else:
                pass  # for draw scenario

            self.CurrentInning = 0
            self.Team1.OutCount = 0
            self.Team2.OutCount = 0
            self.Team1.Score = 0
            self.Team2.Score = 0
            self.Team1.AccumulatedOuts = 0
            self.Team2.AccumulatedOuts = 0
            self.Team1.Pitcher = self.Team1.Pitchers[0]
            self.Team2.Pitcher = self.Team2.Pitchers[0]

        #print(self.Team1wins)
        #print(self.Team2wins)
        #print(self.Team1.Name)
        #print(self.Team2.Name)

        t1wins = self.Team1wins
        t2wins = self.Team2wins

        todays_date = dt.datetime.today().strftime("%d/%m/%Y")

        totalgamewins = t1wins + t2wins

        t1_win_percent = round(t1wins / totalgamewins, 2)
        t2_win_percent = round(t2wins / totalgamewins, 2)

        df = pd.read_csv('game_result_new.csv')

        df.drop(['Unnamed: 0'], axis=1, inplace=True)

        df.to_csv('game_result_old.csv')

        game_series = [todays_date, self.Team1.Name, self.Team1.Pitcher.Name, t1_win_percent, self.Team2.Name,
                       self.Team2.Pitcher.Name, t2_win_percent]

        print(game_series)

        df1 = pd.DataFrame([game_series])

        df1.columns = ['Date', 'away_team', 'away_pitcher', 'away_win_percent', 'home_team', 'home_pitcher',
                       'home_win_percent']

        df2 = df.append(df1, sort=False)

        df2.to_csv('game_result_new.csv')

    #def PrintCurrentResults(self):
        #print('Inning ' + str(self.CurrentInning) + ': '
              #+ self.Team1.Name + " " + str(self.Team1.Score)
              #+ self.Team2.Name + " " + str(self.Team2.Score))


# general utility function

# general utility function
def ResetBases(bases):
    for base in bases:
        base.PlayerHere = None
