#!/usr/bin/env python3
import cProfile

cProfile.run("__import__('outcast').main()", sort="time")
