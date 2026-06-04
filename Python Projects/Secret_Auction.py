bidders = {}
highest_bid = 0
highest_bidder = ""

while True:
    bid = input("What is your name?: ")
    amount = int(input("How much are you bidding?: $"))
    bidders[bid] = amount 

    yes = input("Are there any other bidders? (yes/no) ").lower()
    if yes == "no":
        break
    print("\n" * 20)

for bidder, bid in bidders.items():
    if bid > highest_bid:
        highest_bid = bid
        highest_bidder = bidder
print("\n" * 20)
print(f"Highest bidder: {highest_bidder} with ${highest_bid}")
