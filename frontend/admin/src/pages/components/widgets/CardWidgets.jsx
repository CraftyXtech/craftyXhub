import React from "react";
import Head from "@/layout/head/Head";
import Content from "@/layout/content/Content";
import ActiveUser from "@/components/partials/analytics/active-user/ActiveUser";
import AudienceOverview from "@/components/partials/analytics/audience-overview/AudienceOverview";
import TrafficChannel from "@/components/partials/analytics/traffic-channel/Traffic";
import TrafficDougnut from "@/components/partials/analytics/traffic-dougnut/TrafficDoughnut";
import SessionDevice from "@/components/partials/analytics/session-devices/SessionDevice";
import {
  Block,
  BlockHead,
  BlockHeadContent,
  BlockTitle,
  BackTo,
  PreviewCard,
  CodeBlock,
  PreviewAltCard,
} from "@/components/Component";
import { Card, Col, Row } from "reactstrap";

const CardWidgets = () => {
  return (
    <>
      <Head title="Card Widgets"></Head>
      <Content page="component">
        <BlockHead size="lg" wide="sm">
          <BlockHeadContent>
            <BackTo link="/components" icon="arrow-left">
              Components
            </BackTo>
            <BlockTitle tag="h2" className="fw-normal">
              Card Widgets
            </BlockTitle>
          </BlockHeadContent>
        </BlockHead>

        <Block size="lg">
          <BlockHead>
            <BlockHeadContent>
              <BlockTitle tag="h5">Single Bar Chart</BlockTitle>
              <p>A bar chart provides a way of showing data values represented as vertical bars.</p>
            </BlockHeadContent>
          </BlockHead>
          <PreviewCard>
            <Row>
              <Col md="6">
                <PreviewAltCard>
                  <ActiveUser />
                </PreviewAltCard>
              </Col>
            </Row>
          </PreviewCard>
        </Block>

        <Block size="lg">
          <BlockHead>
            <BlockHeadContent>
              <BlockTitle tag="h5">Solid and Dotted Line Chart</BlockTitle>
              <p>
                A line chart is a way of plotting data points on a line. Often, it is used to show trend data, or the
                comparison of two data sets.
              </p>
            </BlockHeadContent>
          </BlockHead>
          <PreviewCard>
            <Row>
              <Col lg="12">
                <AudienceOverview />
              </Col>
            </Row>
          </PreviewCard>
        </Block>

        <Block size="lg">
          <BlockHead>
            <BlockHeadContent>
              <BlockTitle tag="h5">Multiple Line Chart</BlockTitle>
              <p>A line chart is a way of plotting data points on a line.</p>
            </BlockHeadContent>
          </BlockHead>
          <PreviewCard>
            <Row>
              <Col lg="12">
                <Card className="card-bordered">
                  <TrafficChannel />
                </Card>
              </Col>
            </Row>
          </PreviewCard>
        </Block>

        <Block size="lg">
          <BlockHead>
            <BlockHeadContent>
              <BlockTitle tag="h5">Doughnut Charts</BlockTitle>
              <p>
                Doughnut charts are probably the most commonly used charts. It use to show relational proportions
                between data.
              </p>
            </BlockHeadContent>
          </BlockHead>
          <PreviewCard>
            <Row>
              <Col md="6">
                <PreviewAltCard>
                  <TrafficDougnut />
                </PreviewAltCard>
              </Col>
            </Row>
          </PreviewCard>
        </Block>

        <Block size="lg">
          <BlockHead>
            <BlockHeadContent>
              <BlockTitle tag="h5">Doughnut Charts with icons</BlockTitle>
              <p>
                Doughnut charts are probably the most commonly used charts. It use to show relational proportions
                between data.
              </p>
            </BlockHeadContent>
          </BlockHead>
          <PreviewCard>
            <Row>
              <Col md="6">
                <PreviewAltCard>
                  <SessionDevice />
                </PreviewAltCard>
              </Col>
            </Row>
          </PreviewCard>
        </Block>
      </Content>
    </>
  );
};

export default CardWidgets;
