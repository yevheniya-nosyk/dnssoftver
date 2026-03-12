# Copyright 2026 Yevheniya Nosyk
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

def get_work_dir():
    """Find the path to the project's work directory"""
    # The location of this file
    path = Path(__file__).resolve()
    # Go up intil the git root found
    for parent in path.parents:
        if (parent / ".git").exists():
            return parent


if __name__ == "__main__":

    # Get the work directory of this project
    work_dir = get_work_dir()
