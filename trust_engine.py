class TrustEngine:
    def __init__(self, decay=0.88, prior_alpha=1.0, prior_beta=1.0):
        self.decay = decay
        self.alpha = prior_alpha
        self.beta = prior_beta

    def update(self, outcome: str):
        self.alpha *= self.decay
        self.beta *= self.decay
        if outcome == "win":
            self.alpha += 1
        else:
            self.beta += 1
        return self.trust(), self.variance()

    def trust(self):
        return self.alpha / (self.alpha + self.beta)

    def variance(self):
        a, b = self.alpha, self.beta
        return (a * b) / (((a + b) ** 2) * (a + b + 1))

if __name__ == "__main__":
    te = TrustEngine(decay=0.88)
    outcomes = ["win","win","loss","win","loss","loss","win"]
    for o in outcomes:
        t, v = te.update(o)
        print(f"{o:5s} trust={t:.4f} var={v:.6f}")
    print("OK: trust engine responds to win/loss stream")
