import React, { useState } from "react";
import Head from "@/layout/head/Head";
import Content from "@/layout/content/Content";
import SalesOverview from "@/components/partials/default/sales-overview/SalesOverview";
import { Card } from "reactstrap";
import {
  Block,
  BlockHead,
  BlockHeadContent,
  BlockTitle,
  BlockDes,
  BackTo,
  PreviewCard,
  CodeBlock,
  Row,
  Col,
} from "@/components/Component";
import { DoubleBar, StackedBarChart } from "@/components/partials/charts/default/Charts";

const ChartWidgets = ({ ...props }) => {
  return (
    <>
      <Head title="Chart Widgets" />
      <Content page="component">
        <BlockHead size="lg" className="wide-sm">
          <BlockHeadContent>
            <BackTo link="/components" icon="arrow-left">
              Components
            </BackTo>
            <BlockTitle tag="h2" className="fw-normal">
              Chart Widgets
            </BlockTitle>
            <BlockDes>
              <p className="lead">
                The chart widgets are designed to display the analytics data in a visual way. You can use these widgets
                to display the data in your dashboard.
              </p>
            </BlockDes>
          </BlockHeadContent>
        </BlockHead>

        <Block size="lg">
          <BlockHead>
            <BlockHeadContent>
              <BlockTitle tag="h5">Sales Overview</BlockTitle>
              <p>
                The sales overview widget is used to display the sales data in a visual way. You can use this widget to
                display the sales data in your dashboard.
              </p>
            </BlockHeadContent>
          </BlockHead>
          <PreviewCard>
            <SalesOverview />
          </PreviewCard>
        </Block>

        <Block size="lg">
          <BlockHead>
            <BlockHeadContent>
              <BlockTitle tag="h5">Sales Overview</BlockTitle>
              <p>
                The sales overview widget is used to display the sales data in a visual way. You can use this widget to
                display the sales data in your dashboard.
              </p>
            </BlockHeadContent>
          </BlockHead>
          <PreviewCard>
            <SalesOverview />
          </PreviewCard>
        </Block>
      </Content>
    </>
  );
};

export default ChartWidgets;
