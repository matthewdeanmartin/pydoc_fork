import logging
from pathlib import Path

import tomlkit
from tomlkit.toml_document import TOMLDocument

LOGGER = logging.getLogger(__name__)


def convert_dependencies(poetry_deps: dict) -> list[str]:
    """
    Converts Poetry-style dependencies to PEP 621-style dependencies.

    Args:
        poetry_deps (dict): Dependencies in Poetry format.

    Returns:
        list[str]: Dependencies in PEP 621 format.
    """
    pep621_deps = []
    for package, version_spec in poetry_deps.items():
        if isinstance(version_spec, dict):
            extras = version_spec.get("extras", [])
            markers = version_spec.get("markers", "")
            version = version_spec.get("version", "")

            dep = package
            if extras:
                dep += f"[{','.join(extras)}]"
            if version:
                dep += f" {version}"
            if markers:
                dep += f"; {markers}"
            pep621_deps.append(dep)
        else:
            if version_spec == "*":
                version_spec = ""
            else:
                version_spec = f" {version_spec}"
            pep621_deps.append(f"{package}{version_spec}")
    return pep621_deps


def extract_dependencies(input_path: Path, output_path: Path) -> None:
    """
    Extracts dependencies from a pyproject.toml file and writes them to a new file in PEP 621 format.

    Args:
        input_path (Path): The path to the input pyproject.toml file.
        output_path (Path): The path to the output pyproject_621.toml file.
    """
    LOGGER.info("Reading pyproject.toml from %s", input_path)
    with input_path.open("r", encoding="utf-8") as file:
        pyproject_data = tomlkit.parse(file.read())

    LOGGER.info("Extracting dependencies")
    dependencies_section = TOMLDocument()
    dependencies_section["project"] = {"dependencies": [], "optional-dependencies": {}}

    # Extract the dependencies sections if they exist
    if "tool" in pyproject_data and "poetry" in pyproject_data["tool"]:
        poetry_section = pyproject_data["tool"]["poetry"]
        if "dependencies" in poetry_section:
            dependencies_section["project"]["dependencies"] = convert_dependencies(
                poetry_section["dependencies"]
            )
        if "dev-dependencies" in poetry_section:
            dependencies_section["project"]["optional-dependencies"]["dev"] = (
                convert_dependencies(poetry_section["dev-dependencies"])
            )

    LOGGER.info("Writing extracted dependencies to %s", output_path)
    with output_path.open("w", encoding="utf-8") as file:
        file.write(tomlkit.dumps(dependencies_section))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    input_path = Path("pyproject.toml")
    output_path = Path("pyproject_621.toml")
    extract_dependencies(input_path, output_path)
