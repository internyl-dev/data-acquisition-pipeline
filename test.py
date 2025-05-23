
def require_auth(func):
    auth_users = ['ColdMuffin', 'Tislam', 'Ramen']
    def wrapper(*args, **kwargs): # **kwargs is a dictionary of all the arguments
        if args[0] in auth_users: # *args is a tuple of all the arguments
            func(*args, **kwargs)
    return wrapper


@require_auth
def member_feature(username):
    print(f'This is a member exlcusive print statement, {username}!')

member_feature('ColdMuffin')
member_feature('Bozo')

import asyncio
import time

async def say_after(delay, message):
    await asyncio.sleep(delay)
    print(message)

async def main():
    start = time.time()
    await asyncio.gather(
        say_after(1, "Hello"),
        say_after(2, "World"),
    ) # this will take 2 seconds to run instead of 3
    print(time.time() - start)

asyncio.run(main())