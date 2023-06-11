# Metro-_card_solutions
metro_systems.py - Here we are creating a card for the metro systems. We are using mongodb as database we have card detials, station and travel history in the collections in the metro database Apis under metro_systems.py are:

a. create_station - Here we are creating a staion with certain station code. Assumptions taken are : The station codes are starting from 1001 We dont have cross connection lines for metro, just the straight line

b. create_card - here we are creating a card for a particular user. Assumption taken are : we have card_mapped_id which will be helpful in getting card details once created, in punchin or punch out. it will be used to connect with different apis. email - which will assure that user should be able to purchase only 1 card and we will check if the email is valid or not. balance - by default we will put 500 as balance in the card.

c. get_card_details - this api is used to get the card details. we are using card_mapped_id as argument to get the particular card details

d. punch_in - this api is used to punch in. here we are using email to check the valid user checking whether the car id valid or not blocked or not, either balance is greater than 15 or not and sending proper response to the user. we used redis to store some data which will be useful in punch out.

e. punched_out - this api is used to punch out. here we are using redis to read the stored file. we are checking and calulating the fare and deducting from the balance in the card. we are storing the travel history in the database as well.

f. recharge - here we are recharging with some amount in the card.
