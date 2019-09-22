# -*- coding: utf-8 -*-
"""Common fixtures for tests"""
import pytest
from .context import Repo


@pytest.fixture
def blank_repo():
    """An blank git repo with just one commit"""
    return Repo()
