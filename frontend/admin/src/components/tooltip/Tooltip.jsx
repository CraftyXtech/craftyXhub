import React, { useRef } from "react";
import Icon from "@/components/icon/Icon";
import { UncontrolledTooltip } from "reactstrap";

const TooltipComponent = ({
  iconClass,
  icon,
  id,
  direction,
  text,
  containerClassName,
  children,
  ...props
}) => {
  const targetRef = useRef(null);

  let trigger = null;

  if (children) {
    // When children are provided, treat the child as the trigger element.
    const child = React.Children.only(children);
    trigger = React.cloneElement(child, {
      ref: targetRef,
      ...(id ? { id } : {}),
      ...child.props,
    });
  } else if (props.tag) {
    const Tag = props.tag;
    trigger = (
      <Tag className={containerClassName} id={id} ref={targetRef}>
        <Icon className={iconClass || ""} name={icon}></Icon>
      </Tag>
    );
  } else {
    trigger = (
      <Icon
        className={iconClass || ""}
        name={icon}
        id={id}
        ref={targetRef}
      ></Icon>
    );
  }

  return (
    <React.Fragment>
      {trigger}
      <UncontrolledTooltip
        autohide={false}
        placement={direction}
        target={targetRef}
      >
        {text}
      </UncontrolledTooltip>
    </React.Fragment>
  );
};

export default TooltipComponent;
