#!/usr/bin/env python3
import cProfile

cProfile.run("__import__('cast_away').main()", sort="time")
