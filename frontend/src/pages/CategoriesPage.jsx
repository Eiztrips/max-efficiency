import { Container, Flex, Typography, CellList, CellSimple, CellHeader, Counter } from "@maxhub/max-ui";

const CategoriesPage = () => {
  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px" }}>
    <Flex direction="column" gap={16} style={{ width: "100%" }}>
      <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
        <Typography.Headline variant="large-strong">Категории</Typography.Headline>
      </Container>

      <CellList mode="island" header={<CellHeader>Мои категории</CellHeader>} style={{ width: "100%" }}>
        <CellSimple
          showChevron
          title="Работа"
          subtitle="Рабочие задачи"
          after={<Counter value={5} rounded />}
          onClick={() => {}}
        />
        <CellSimple
          showChevron
          title="Личное"
          subtitle="Личные дела"
          after={<Counter value={3} rounded />}
          onClick={() => {}}
        />
        <CellSimple
          showChevron
          title="Покупки"
          subtitle="Список покупок"
          after={<Counter value={7} rounded />}
          onClick={() => {}}
        />
      </CellList>
    </Flex>
    </div>
  );
};

export default CategoriesPage;
