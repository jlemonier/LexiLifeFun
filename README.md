# LexiLifeFun
LexiLife.io Lighting &amp

See instructions in lexi.py

# Set 4 environment variables: lexi_username, lexi_password, lexi_client_id, lexi_client_secret
# set lexi_username=jason@fun.com
# set lexi_password=LoveLexi
# set lexi_client_id=

parameter_hub_name = "Ratto Kickstarter"  # This helps the code choose from your list of hubs
user_guid          = "1e8e23d4-5288-485c-bff0-b01d4b4b1b00"  # From Cloud Api Tester

python lexi_fun.py
  ==> will login, get auth token, find ip for hub(s) for your Lexi Login, and then use IP for Hub name specified to control lights.
  
  ==> Then based on "light type" (such as 134 for Candle), the lights will be rotated by that type.  Not based on groups yet.
