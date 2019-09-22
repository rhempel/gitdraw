# Gitdraw

A simple tool for generating git graphs from a set of git commands

## Getting Started

### Installing

Install using pip
```bash
pip install gitdraw
```

## Running the tests

The project tests are run with `pytest` automatically in pipelines. To run 
them manually find the `pytest` script command in [.gitlab-ci.yml](.gitlab-ci.yml) 
and run it from the root of the repository.

```yaml
pytest:
  stage: Test
  script:
  - <this command>
```

## Running the tool

The tool is run using `python3.7`. For help text use:
```bash
python3.7 -m gitdraw.__main__ -h
```

## Built With

See [requirements.txt](requirements.txt) for the full details of external
packages. A number are used just for testing so won't be required if you
don't intend to run the tests


## Examples

The following examples are autogeneraed from pipelines

### [Simple Branch](samples/simple_branch.txt)

<img src="https://gitlab.com/broster/gitdraw/-/jobs/artifacts/master/raw/samples/simple_branch.svg?job=samples"  width="1000" height="1000">

### [Merges](samples/merges.txt)

![graph2](https://gitlab.com/broster/gitdraw/-/jobs/artifacts/master/raw/samples/merges.svg?job=samples)

### [Forward Merges](samples/forward_merges.txt)

![graph3](https://gitlab.com/broster/gitdraw/-/jobs/artifacts/master/raw/samples/forward_merges.svg?job=samples)

### [Multiple Brances](samples/multiple_branches.txt)

![graph4](https://gitlab.com/broster/gitdraw/-/jobs/artifacts/master/raw/samples/multiple_branches.svg?job=samples)
