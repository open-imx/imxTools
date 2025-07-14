from loguru import logger
from lxml import etree
from lxml.etree import QName, _Element

from src.imxTools.settings import config


def add_comment(parent: _Element, child: _Element | None, comment: str):
    if child:
        parent.insert(parent.index(child), etree.Comment(comment))
    else:
        new_parent = parent.getparent()
        child = parent
        if new_parent:
            new_parent.insert(new_parent.index(child), etree.Comment(comment))


def get_all_elements_by_name(element: _Element, element_name: str) -> list[_Element]:
    return element.xpath(f'.//*[local-name()="{element_name}"]')


def get_elements_by_name(element: _Element, element_name: str) -> list[_Element]:
    return element.xpath(f'./*[local-name()="{element_name}"]')


def get_all_elements_containing_attribute(
    element: _Element, attribute_name: str, value: str | None = None
) -> list[_Element]:
    if value:
        return element.xpath(f'..//*[{attribute_name}="{value}"]')
    return element.xpath(f"..//*[{attribute_name}]")


def set_attribute(element: _Element, attribute_name: str, value: str):
    old_value = element.get(attribute_name.replace("@", ""))
    element.set(attribute_name.replace("@", ""), value)

    if config.ADD_COMMENTS:
        add_comment(
            element,
            None,
            f"Attribute element below changed {attribute_name} old: {old_value} new: {value}",
        )


def set_element_text(element: _Element, element_name: str, value: str):
    temp = get_elements_by_name(element, element_name)
    if temp:
        old_value = temp[0].text
        temp[0].text = value
        if config.ADD_COMMENTS:
            add_comment(
                temp[0],
                None,
                f"_Element text below changed {element_name} old: {old_value} new: {value}",
            )


def get_parent_and_target(
    element: _Element, path_split: list[str]
) -> tuple[_Element, str]:
    parent = element
    for idx, element_name in enumerate(path_split[:-1]):
        elements = get_elements_by_name(parent, element_name)
        if len(elements) > 1:
            try:
                parent = elements[int(path_split[idx + 1])]
            except Exception:
                raise ValueError(
                    f'{".".join(path_split)} index "{int(path_split[idx + 1])}" out of range'
                )
        else:
            if elements:
                parent = elements[0]
    return parent, path_split[-1] if len(path_split) != 0 else ""


def handle_attribute(
    parent: _Element, attribute_name: str, value: str, old_value: str | None
):
    attr_key = attribute_name.replace("@", "")
    if old_value:
        if parent.attrib.get(attr_key) == old_value:
            set_attribute(parent, attribute_name, value)
        elif not parent.attrib.get(attr_key):
            raise ValueError(f"Attribute not found: {attr_key}")
        else:
            raise ValueError(
                f"Attribute mismatch: {attr_key} has value {parent.attrib.get(attr_key)}"
            )
    else:
        if attr_key not in parent.attrib:
            set_attribute(parent, attribute_name, value)


def handle_element(
    parent: _Element, element_name: str, value: str, old_value: str | None
):
    elements = get_elements_by_name(parent, element_name)
    if elements and elements[0].text == old_value:
        set_element_text(parent, element_name, value)
    else:
        raise ValueError("Mismatch in old value for element text.")


def set_attribute_or_element_by_path(
    puic_object: _Element, path: str, value: str, old_value: str | None
):
    path_split = path.split(".")
    path_split = [_.replace("gml:", "") for _ in path_split if isinstance(_, str)]
    if path_split[-1].startswith("@"):  # Attribute case
        parent, attribute_name = get_parent_and_target(puic_object, path_split)
        handle_attribute(parent, attribute_name, value, old_value)
    else:  # _Element case
        parent, element_name = get_parent_and_target(puic_object, path_split)
        handle_element(parent, element_name, value, old_value)


def delete_attribute_if_matching(puic_object: _Element, path: str, value: str):
    path_split = path.split(".")
    attribute_name = path_split[-1]
    if not attribute_name.startswith("@"):  # Ensure it's an attribute
        raise ValueError("Path must end with an attribute (e.g., '@id').")

    parent, _ = get_parent_and_target(puic_object, path_split[:-1])
    attribute_name = attribute_name.replace("@", "")
    if parent.attrib.get(attribute_name) == value:
        del parent.attrib[attribute_name]
        if config.ADD_COMMENTS:
            add_comment(parent, None, f"Attribute {attribute_name} removed removed")
    else:
        raise ValueError(
            f"Attribute '{attribute_name}' not found as attribute object'."
        )


def delete_element(element: _Element):
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)
        if config.ADD_COMMENTS:
            add_comment(parent, None, f"_Element {element} removed")


def set_metadata(
    node: _Element,
    set_meta_parents: bool = False,
    replace_metadata: bool = True,
    add_metadata: bool = True,
    metadata_source: str = "DV",
    metadata_origin: str = "Unknown",
    registration_time: str | None = None,
):
    set_metadata_node(
        node,
        replace_metadata,
        add_metadata,
        metadata_source,
        metadata_origin,
        registration_time,
    )

    if set_meta_parents:
        parent = node.getparent()
        while parent is not None:
            puic_ = parent.get("puic")
            prorail_tags = {
                "{http://www.prorail.nl/IMSpoor}Project",
                "{http://www.prorail.nl/IMSpoor}Situation",
                "{http://www.prorail.nl/IMSpoor}SignalingDesign",
            }

            if parent.tag in prorail_tags:
                break

            elif puic_ is not None:
                set_metadata_node(
                    parent,
                    replace_metadata,
                    add_metadata,
                    metadata_source,
                    metadata_origin,
                    registration_time,
                )
                logger.success(f"metadata for parent {puic_} set")
            parent = parent.getparent()


def set_metadata_node(
    node: _Element,
    replace_metadata: bool = True,
    add_metadata: bool = True,
    metadata_source: str = "DV",
    metadata_origin: str = "Unknown",
    registration_time: str | None = None,
):
    metadata = node.find(".//{http://www.prorail.nl/IMSpoor}Metadata")
    if metadata is None:
        logger.warning("No metadata node present, metadata not set!")
        return

    if replace_metadata:
        source_value = metadata_source
    else:
        source_value = str(metadata.get("source", ""))

        if add_metadata:
            if not source_value.endswith(metadata_source):
                source_value = f"{source_value}_{metadata_source}"

    metadata.set("source", source_value)
    metadata.set("originType", metadata_origin)

    if registration_time is not None:
        metadata.set("registrationTime", registration_time)

    if config.ADD_COMMENTS:
        add_comment(node, metadata, "MetadataChanged")

    puic_ = node.get("puic")
    logger.success(f"metadata for {puic_} set")


def create_element_under(node: _Element, under_element: str, xml_str: str):
    xml_to_insert = etree.fromstring(xml_str)
    under_node = node.findall(f"{{http://www.prorail.nl/IMSpoor}}{under_element}")
    under_node[0].addnext(xml_to_insert)

    puic_ = node.get("puic")
    set_metadata(node)
    logger.success(f"metadata for {puic_} set")


def delete_element_that_matches(node: _Element, xml_str: str):
    xml_to_insert = etree.fromstring(xml_str)

    tag_raw = xml_to_insert.tag
    if isinstance(tag_raw, QName):
        tag = tag_raw.localname
    elif isinstance(tag_raw, str | bytes | bytearray):
        tag_str = (
            tag_raw.decode() if isinstance(tag_raw, bytes | bytearray) else tag_raw
        )
        tag = tag_str.split("}")[-1] if "}" in tag_str else tag_str
    else:
        raise TypeError(f"Unsupported tag type: {type(tag_raw)}")

    conditions = [f"@{k}='{v}'" for k, v in xml_to_insert.attrib.items()]
    condition_str = f"{' and '.join(conditions)}" if conditions else ""
    xpath_query = (
        f".//*[local-name() = '{tag}'"
        + (f" and {condition_str}" if condition_str else "")
        + "]"
    )

    node_to_remove = node.xpath(xpath_query)
    if not node_to_remove:
        logger.warning(
            f"No element found for deletion with tag '{tag}' and attributes {xml_to_insert.attrib}"
        )
        return

    parent = node_to_remove[0].getparent()
    if parent is not None:
        parent.remove(node_to_remove[0])
        puic_ = parent.get("puic")
        set_metadata(parent)
        logger.success(f"metadata for {puic_} set")
    else:
        logger.warning("Element has no parent and could not be removed.")


def get_imx_version(imx_tree: _Element) -> str:
    imx_version = imx_tree.findall(".//*[@imxVersion]")
    assert len(imx_version) == 1, (
        "There should be exactly one imxVersion element in the XML file"
    )
    return f"{imx_version[0].get('imxVersion')}"
