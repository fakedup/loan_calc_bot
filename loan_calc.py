class Loan():
    """
    Class to hold options of a loan: sum, payment, rate and term.
    """
    def __init__(self):
        self.summ = 0
        self.payment = 0
        self.rate = 0
        self.term = 0
        self.str_term = ''
        self.is_consistent = False

    def calc_payment(self):
        if self.is_consistent:
            return self.payment
        elif all([self.summ, self.rate, self.term]) > 0:
            self.payment = (self.summ * self.rate/12)/(1-(1+self.rate/12)**(1-self.term))
            self.is_consistent = True
            return self.payment
        else:
            raise AttributeError ('Some parameters are missing or zero. Unable to calculate.')

    def calc_summ(self):
        if self.is_consistent:
            return self.summ
        elif all([self.payment, self.rate, self.term]) > 0:
            self.summ = self.payment*(1-1/((1+self.rate/12)**self.term))*self.rate/12
            self.is_consistent = True
            return self.summ
        else:
            raise AttributeError ('Some parameters are missing or zero. Unable to calculate.')

    def calc_rate(self):
        if self.is_consistent:
            return self.rate
        elif all([self.summ, self.payment, self.term]) > 0:
            self.rate = 0.1
            self.is_consistent = True
            return self.summ
        else:
            raise AttributeError ('Some parameters are missing or zero. Unable to calculate.')       

    def calc_term(self):
        pass

    def set_summ(self, summ):
        self.summ = summ
        self.is_consistent = False

    def set_payment(self, payment):
        self.payment = payment
        self.is_consistent = False

    def set_rate(self, rate):
        self.rate = rate
        self.is_consistent = False

    def set_term(self, term):
        self.term = term
        self.is_consistent = False

    def get_loan_parameters(self):
        text = 'Sum: {0:,.2f},\npayment: {1:,.2f},\nrate: {2:.2f}%,\nterm: {3}.'
        if self.is_consistent:
            return text.format(self.summ, self.payment, self.rate*100, self.term).replace(',', ' ')
        else:
            return 'Calculation isn\'t finished! Current data:\n' + text.format(self.summ, self.payment, self.rate*100, self.term)

    def get_log_string(self):
        return ";".join([str(el) for el in [self.summ, self.payment, self.rate, self.term]])