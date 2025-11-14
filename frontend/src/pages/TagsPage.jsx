import { Container, Flex, Typography, CellList, CellSimple, CellHeader } from "@maxhub/max-ui";

const TagsPage = () => {
  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px" }}>
    <Flex direction="column" gap={16} style={{ width: "100%" }}>
      <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
        <Typography.Headline variant="large-strong">Теги</Typography.Headline>
      </Container>

      <CellList mode="island" header={<CellHeader>Все теги</CellHeader>} style={{ width: "100%" }}>
        <CellSimple
          showChevron
          title="Срочно"
          onClick={() => {}}
        />
        <CellSimple
          showChevron
          title="Важно"
          onClick={() => {}}
        />
        <CellSimple
          showChevron
          title="Здоровье"
          onClick={() => {}}
        />
        <CellSimple
          showChevron
          title="Звонки"
          onClick={() => {}}
        />
      </CellList>
    </Flex>
    </div>
  );
};

export default TagsPage;
